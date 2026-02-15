import os
import sys
import json
import re
import time
from openai import OpenAI
import sc2reader

MODELS_CONFIG = [
    {
        "name": "",
        "api_key": os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"),
        "base_url": "",
        "model_id": "",
        "temperature": 0
    },
]

WORKER_NAMES = {'SCV', 'Probe', 'Drone', 'MULE'}
UNIT_COSTS = {
    'SCV': {'m': 50, 'g': 0, 's': 1}, 'Marine': {'m': 50, 'g': 0, 's': 1},
    'Marauder': {'m': 100, 'g': 25, 's': 2}, 'SiegeTank': {'m': 150, 'g': 125, 's': 3},
    'Medivac': {'m': 100, 'g': 100, 's': 2}, 'Thor': {'m': 300, 'g': 200, 's': 6},
    'VikingFighter': {'m': 150, 'g': 75, 's': 2}, 'Liberator': {'m': 150, 'g': 150, 's': 3},
    'Ghost': {'m': 150, 'g': 125, 's': 2}, 'Hellion': {'m': 100, 'g': 0, 's': 2},
    'WidowMine': {'m': 75, 'g': 25, 's': 2}, 'Cyclone': {'m': 150, 'g': 100, 's': 3},
    'Raven': {'m': 100, 'g': 200, 's': 2}, 'Banshee': {'m': 150, 'g': 100, 's': 3},
    'Battlecruiser': {'m': 400, 'g': 300, 's': 6}, 'Reaper': {'m': 50, 'g': 50, 's': 1},
    'Probe': {'m': 50, 'g': 0, 's': 1}, 'Zealot': {'m': 100, 'g': 0, 's': 2},
    'Stalker': {'m': 125, 'g': 50, 's': 2}, 'Immortal': {'m': 275, 'g': 100, 's': 4},
    'Colossus': {'m': 300, 'g': 200, 's': 6}, 'Carrier': {'m': 350, 'g': 250, 's': 6},
    'Archon': {'m': 175, 'g': 275, 's': 4}, 'VoidRay': {'m': 250, 'g': 150, 's': 4},
    'Sentry': {'m': 50, 'g': 100, 's': 2}, 'Adept': {'m': 100, 'g': 25, 's': 2},
    'HighTemplar': {'m': 50, 'g': 150, 's': 2}, 'DarkTemplar': {'m': 125, 'g': 125, 's': 2},
    'Oracle': {'m': 150, 'g': 150, 's': 3}, 'Tempest': {'m': 250, 'g': 175, 's': 5},
    'WarpPrism': {'m': 200, 'g': 0, 's': 2}, 'Observer': {'m': 25, 'g': 75, 's': 1},
    'Drone': {'m': 50, 'g': 0, 's': 1}, 'Zergling': {'m': 25, 'g': 0, 's': 0.5},
    'Roach': {'m': 75, 'g': 25, 's': 2}, 'Hydralisk': {'m': 100, 'g': 50, 's': 2},
    'Ravager': {'m': 100, 'g': 100, 's': 3}, 'Lurker': {'m': 150, 'g': 150, 's': 3},
    'Mutalisk': {'m': 100, 'g': 100, 's': 2}, 'Corruptor': {'m': 150, 'g': 100, 's': 2},
    'Ultralisk': {'m': 300, 'g': 200, 's': 6}, 'Queen': {'m': 150, 'g': 0, 's': 2},
    'Baneling': {'m': 50, 'g': 25, 's': 0.5}, 'Viper': {'m': 100, 'g': 200, 's': 3},
    'SwarmHost': {'m': 100, 'g': 75, 's': 3}, 'BroodLord': {'m': 300, 'g': 250, 's': 4},
    'Overlord': {'m': 100, 'g': 0, 's': 0}
}


def call_llm_api(config, prompt, count):
    model_friendly_name = config['name']
    try:
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        print(f"     ... [{model_friendly_name}] Requesting ({count} data points) ...")

        # PAPER PROMPT ALIGNMENT: DWE System Prompt
        system_prompt = (
            "Role: StarCraft II Real-time Momentum Analyst.\n"
            "Task: Generate a continuous win-probability curve based on material causality.\n"
            "Definitions: Material Reality: Evaluating 17 features including resource loss ratios and combat efficiency. "
            "Predictive Asymptote: Mathematical convergence towards 1.0 or 0.0 as duration increases.\n"
            "Format Requirement: You must output ONLY a raw JSON Array of floats."
        )

        response = client.chat.completions.create(
            model=config['model_id'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()
        content_clean = content.replace("```json", "").replace("```", "").strip()

        if "</think>" in content_clean:
            content_clean = content_clean.split("</think>")[-1].strip()
        if not content_clean.startswith("["):
            start_idx = content_clean.find("[")
            if start_idx != -1:
                content_clean = content_clean[start_idx:]

        predictions = []
        try:
            predictions = json.loads(content_clean)
        except json.JSONDecodeError:
            nums = re.findall(r"\b0\.\d+\b|\b1\.0\b|\b0\b", content_clean)
            predictions = [float(n) for n in nums]

        if len(predictions) < count:
            print(f"     [Warning] {model_friendly_name} returned insufficient data, padding with 0.5")
            predictions.extend([0.5] * (count - len(predictions)))

        return predictions[:count]

    except Exception as e:
        print(f"     [API Error] {model_friendly_name} failed: {e}")
        return [0.5] * count


def get_batch_win_rates(batch_states, p1_name, p2_name, config):
    data_lines = []
    for state in batch_states:
        line = (
            f"[T={state['time']}s] "
            f"P1({p1_name}):Eco({state['p1']['min_rate']}/{state['p1']['gas_rate']}),Army({state['p1']['army_value']}),KD({state['p1']['army_killed_val']}/{state['p1']['army_lost_val']}) | "
            f"P2({p2_name}):Eco({state['p2']['min_rate']}/{state['p2']['gas_rate']}),Army({state['p2']['army_value']}),KD({state['p2']['army_killed_val']}/{state['p2']['army_lost_val']})"
        )
        data_lines.append(line)

    data_block = "\n".join(data_lines)
    count = len(batch_states)

    prompt = f"""
Input Data ({count} timestamps):
{data_block}

Task: Output a raw JSON Array of floats representing Player 1's win probability (0.0 to 1.0) for each timestamp.
Format: time: [s], win.prob: [0-1], primary driver: [Feature]
Constraint: For this batch interface, return ONLY the probability floats in a JSON array.
"""
    return call_llm_api(config, prompt, count)


def extract_replay_data(replay_path):
    if not os.path.exists(replay_path):
        return None, None, None, None, []
    try:
        replay = sc2reader.load_replay(replay_path, load_level=4)
    except Exception as e:
        print(f"Read Error: {e}")
        return None, None, None, None, []

    if len(replay.players) < 2:
        return None, None, None, None, []

    p1, p2 = replay.players[0], replay.players[1]
    p1_id, p2_id = p1.pid, p2.pid

    stats = {
        p.pid: {'res': [], 'army_val': 0, 'units': {}, 'killed_army': 0, 'lost_army': 0, 'killed_eco': 0, 'lost_eco': 0}
        for p in [p1, p2]}
    unit_owner_map, unit_type_map = {}, {}

    for event in replay.tracker_events:
        if isinstance(event, sc2reader.events.tracker.PlayerStatsEvent) and event.pid in stats:
            stats[event.pid]['res'].append(
                {'t': event.second, 'mr': event.minerals_collection_rate, 'gr': event.vespene_collection_rate,
                 'ms': event.minerals_current, 'gs': event.vespene_current, 'fu': event.food_used,
                 'fc': event.food_made, 'av': stats[event.pid]['army_val'], 'ka': stats[event.pid]['killed_army'],
                 'la': stats[event.pid]['lost_army'], 'ke': stats[event.pid]['killed_eco'],
                 'le': stats[event.pid]['lost_eco']})
        if isinstance(event, (sc2reader.events.tracker.UnitBornEvent, sc2reader.events.tracker.UnitInitEvent)):
            p = getattr(event, 'control_player', getattr(event, 'upkeep_player', None))
            if p and p.pid in stats:
                u_name = getattr(event, 'unit_type_name', '')
                unit_owner_map[event.unit_id], unit_type_map[event.unit_id] = p.pid, u_name
                if u_name in UNIT_COSTS:
                    val = UNIT_COSTS[u_name]['m'] + UNIT_COSTS[u_name]['g'] * 1.5
                    if u_name not in WORKER_NAMES: stats[p.pid]['army_val'] += val; stats[p.pid]['units'][
                        event.unit_id] = val
        if isinstance(event, sc2reader.events.tracker.UnitDiedEvent):
            victim_pid, killer_pid, u_name = unit_owner_map.get(event.unit_id), getattr(event.killer, 'pid',
                                                                                        None), unit_type_map.get(
                event.unit_id, '')
            if victim_pid in stats and u_name in UNIT_COSTS:
                val, is_worker = UNIT_COSTS[u_name]['m'] + UNIT_COSTS[u_name]['g'] * 1.5, u_name in WORKER_NAMES
                if is_worker:
                    stats[victim_pid]['lost_eco'] += val
                else:
                    stats[victim_pid]['lost_army'] += val
                    if event.unit_id in stats[victim_pid]['units']: stats[victim_pid]['army_val'] -= stats[victim_pid][
                        'units'].pop(event.unit_id)
                if killer_pid in stats and killer_pid != victim_pid:
                    if is_worker:
                        stats[killer_pid]['killed_eco'] += val
                    else:
                        stats[killer_pid]['killed_army'] += val

    full_timeline = []
    game_end = int(replay.game_length.total_seconds())
    for t in range(0, game_end, 7):
        current_state, has_data = {'time': t}, True
        for p in [p1, p2]:
            res = next((item for item in reversed(stats[p.pid]['res']) if item['t'] <= t), None)
            if res:
                player_key = 'p1' if p.pid == p1.pid else 'p2'
                current_state[player_key] = {'min_rate': res['mr'], 'gas_rate': res['gr'], 'min_saved': res['ms'],
                                             'gas_saved': res['gs'], 'food_used': res['fu'], 'food_cap': res['fc'],
                                             'army_value': res['av'], 'army_killed_val': res['ka'],
                                             'army_lost_val': res['la'], 'eco_killed_val': res['ke'],
                                             'eco_lost_val': res['le']}
            else:
                has_data = False;
                break
        if has_data: full_timeline.append(current_state)

    return p1.name, p1_id, p2.name, p2_id, full_timeline


if __name__ == "__main__":
    INPUT_FOLDER = "./replays"
    OUTPUT_FOLDER = "./experiment_results"

    if len(sys.argv) >= 2:
        INPUT_FOLDER = sys.argv[1]

    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Input folder does not exist -> {INPUT_FOLDER}")
        sys.exit(1)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    replay_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".SC2Replay")]

    if not replay_files:
        print(f"No .SC2Replay files found in {INPUT_FOLDER}")
        sys.exit(0)

    print(f"Found {len(replay_files)} replays. Models to test: {len(MODELS_CONFIG)}")

    for replay_file in replay_files:
        replay_path = os.path.join(INPUT_FOLDER, replay_file)
        replay_name_no_ext = os.path.splitext(replay_file)[0]

        print(f"\n>>> [Processing] {replay_file}")
        p1_name, p1_id, p2_name, p2_id, full_timeline = extract_replay_data(replay_path)

        if not full_timeline:
            print(f"  -> Invalid data, skipping.")
            continue

        for config in MODELS_CONFIG:
            model_name = config['name']
            output_filename = f"{model_name}_{replay_name_no_ext}.json"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            if os.path.exists(output_path):
                print(f"  -> [{model_name}] Results exist, skipping.")
                continue

            predictions_log = []
            BATCH_DURATION = 300
            current_batch = []
            batch_index = 0
            total_states = len(full_timeline)

            print(f"  -> Model start: {model_name} ...")

            for i, game_state in enumerate(full_timeline):
                current_batch.append(game_state)
                current_time = game_state['time']

                is_batch_full = current_time >= (batch_index + 1) * BATCH_DURATION
                is_last_item = (i == total_states - 1)

                if (is_batch_full and current_batch) or (is_last_item and current_batch):
                    p1_win_rates = get_batch_win_rates(current_batch, p1_name, p2_name, config)

                    for state, wr in zip(current_batch, p1_win_rates):
                        prediction_data = {
                            "game_time_seconds": state['time'],
                            "model_used": model_name,
                            "player1_id": p1_id,
                            "p1_win_rate": wr
                        }
                        predictions_log.append(prediction_data)

                    current_batch = []
                    if is_batch_full:
                        batch_index += 1

            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(predictions_log, f, indent=4)
                print(f"     Saved: {output_filename}")
            except Exception as e:
                print(f"     Save Failed: {e}")

    print("\n" + "=" * 60)
    print(f"All tasks completed. Results in: {OUTPUT_FOLDER}")