import sc2reader
import json
import os
import re
from collections import defaultdict
from openai import OpenAI

MODELS_CONFIG = [
    {
        "name": "",
        "api_key": os.environ.get("DASHSCOPE_API_KEY", "YOUR_API_KEY_HERE"),
        "base_url": "",
        "model_id": "",
        "temperature": 0
    }
]

REPLAY_FOLDER_PATH = "replays"
OUTPUT_FOLDER_PATH = "./dwp_results"
CHECKPOINTS = [2 * 60, 4 * 60, 6 * 60, 8 * 60, 10 * 60]


def get_unit_name(unit):
    return unit.name if unit and unit.name else "UnknownUnit"


def parse_replay_states(replay_path):
    print(f"--> [Parsing] {os.path.basename(replay_path)} ...")
    try:
        replay = sc2reader.load_replay(replay_path, load_level=4)
    except Exception as e:
        print(f"!!! Parsing Failed: {e}")
        return None, None, None

    players_state = {}
    for player in replay.players:
        if player.is_observer or player.is_referee:
            continue
        players_state[player.pid] = {
            'name': player.name,
            'race': getattr(player, 'play_race', 'Unknown'),
            'units': defaultdict(int),
            'upgrades': [],
            'resources': {'minerals': 0, 'vespene': 0, 'supply_used': 0, 'supply_total': 0}
        }

    snapshots = []
    checkpoint_idx = 0

    for event in replay.events:
        if checkpoint_idx >= len(CHECKPOINTS):
            break

        current_time_seconds = event.second
        if current_time_seconds >= CHECKPOINTS[checkpoint_idx]:
            snapshot = {
                'time_min': CHECKPOINTS[checkpoint_idx] // 60,
                'players': json.loads(json.dumps(players_state))
            }
            snapshots.append(snapshot)
            checkpoint_idx += 1

        if event.name == 'PlayerStatsEvent':
            pid = event.player.pid
            if pid in players_state:
                players_state[pid]['resources']['minerals'] = event.minerals_current
                players_state[pid]['resources']['vespene'] = event.vespene_current
                players_state[pid]['resources']['supply_used'] = event.food_used
                players_state[pid]['resources']['supply_total'] = event.food_made

        elif event.name == 'UnitBornEvent' and event.unit_controller:
            pid = event.unit_controller.pid
            u_name = get_unit_name(event.unit)
            if pid in players_state:
                players_state[pid]['units'][u_name] += 1

        elif event.name == 'UnitDoneEvent' and event.unit and event.unit.owner:
            pid = event.unit.owner.pid
            u_name = get_unit_name(event.unit)
            if pid in players_state:
                players_state[pid]['units'][u_name] += 1

        elif event.name == 'UnitDiedEvent' and event.unit and event.unit.owner:
            pid = event.unit.owner.pid
            u_name = get_unit_name(event.unit)
            if pid in players_state and players_state[pid]['units'][u_name] > 0:
                players_state[pid]['units'][u_name] -= 1

        elif event.name == 'UpgradeCompleteEvent' and event.player:
            pid = event.player.pid
            upgrade_name = event.upgrade_type_name
            if pid in players_state and upgrade_name not in players_state[pid]['upgrades']:
                players_state[pid]['upgrades'].append(upgrade_name)

    real_winner_pid = -1
    if replay.winner:
        if hasattr(replay.winner, 'players') and len(replay.winner.players) > 0:
            real_winner_pid = replay.winner.players[0].pid
        elif hasattr(replay.winner, 'pid'):
            real_winner_pid = replay.winner.pid

    real_winner_name = "Unknown"
    if real_winner_pid != -1:
        if str(real_winner_pid) in players_state:
            real_winner_name = players_state[str(real_winner_pid)]['name']
        elif real_winner_pid in players_state:
            real_winner_name = players_state[real_winner_pid]['name']

    return snapshots, real_winner_pid, real_winner_name


def generate_prompt(snapshot):
    time_min = snapshot['time_min']
    p_data = snapshot['players']
    pids = list(p_data.keys())
    if len(pids) < 2: return None
    p1_id, p2_id = pids[0], pids[1]
    p1 = p_data[p1_id]
    p2 = p_data[p2_id]

    # PAPER PROMPT ALIGNMENT: DWP User Prompt
    prompt = f"""
Timestamp: {time_min} minutes
[Player ID: {p1_id}] Name: {p1['name']} (Race: {p1['race']})
- Resources: M {p1['resources']['minerals']}, G {p1['resources']['vespene']}, Supply {p1['resources']['supply_used']}/{p1['resources']['supply_total']}
- Units: {json.dumps(p1['units'])}
- Upgrades: {json.dumps(p1['upgrades'])}

[Player ID: {p2_id}] Name: {p2['name']} (Race: {p2['race']})
- Resources: M {p2['resources']['minerals']}, G {p2['resources']['vespene']}, Supply {p2['resources']['supply_used']}/{p2['resources']['supply_total']}
- Units: {json.dumps(p2['units'])}
- Upgrades: {json.dumps(p2['upgrades'])}

Task: Predict terminal match outcome from independent temporal snapshots.
Definitions: Strategic Foresight: Inferring victory from sparse data. Resource Quantification: Estimating win probability.
Format: timestamp: [s], winner: [Player ID], confidence: [0-1], rationale: [Analysis]
Restriction: Return ONLY the Player ID of the winner.
"""
    return prompt


def query_llm(client, model_config, prompt):
    if not prompt: return "Error"
    try:
        # PAPER PROMPT ALIGNMENT: DWP System Prompt
        system_prompt = "Role: StarCraft II Strategic Forecasting Expert."

        response = client.chat.completions.create(
            model=model_config["model_id"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=model_config["temperature"]
        )
        prediction = response.choices[0].message.content.strip()
        return prediction.replace("Player", "").replace("player", "").replace("ID", "").strip()
    except Exception as e:
        print(f"  [API Error] {model_config['name']} failed: {e}")
        return "Error"


def get_player_name_by_pid(players_dict, pid):
    if str(pid) in players_dict: return players_dict[str(pid)]['name']
    if pid in players_dict: return players_dict[pid]['name']
    return "Unknown"


def process_single_match_with_model(snapshots, real_winner_pid, real_winner_name, match_name, model_config):
    display_name = model_config["name"]
    print(f"  > Model [{display_name}] predicting {match_name} ...")

    client = OpenAI(
        api_key=model_config["api_key"],
        base_url=model_config["base_url"]
    )

    results = {
        "match_name": match_name,
        "model_name": display_name,
        "real_winner_id": real_winner_pid,
        "real_winner_name": real_winner_name,
        "predictions": []
    }

    correct_count = 0

    for snapshot in snapshots:
        time_mark = snapshot['time_min']
        prompt = generate_prompt(snapshot)
        if prompt is None: continue

        predicted_pid_str = query_llm(client, model_config, prompt)

        predicted_pid = -1
        try:
            nums = re.findall(r'\d+', predicted_pid_str)
            if nums:
                predicted_pid = int(nums[0])
        except:
            pass

        predicted_name = get_player_name_by_pid(snapshot['players'], predicted_pid)
        is_correct = (predicted_pid == real_winner_pid)
        if is_correct: correct_count += 1

        results["predictions"].append({
            "time_min": time_mark,
            "predicted_winner_id": predicted_pid,
            "is_correct": is_correct
        })

    accuracy = correct_count / len(snapshots) if snapshots else 0
    results["accuracy"] = accuracy

    output_filename = f"{display_name}_{match_name}.json"
    output_path = os.path.join(OUTPUT_FOLDER_PATH, output_filename)

    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"    Done. Accuracy: {accuracy:.2%} -> Saved: {output_filename}")


def main():
    if not os.path.exists(OUTPUT_FOLDER_PATH):
        os.makedirs(OUTPUT_FOLDER_PATH)
        print(f"Created output dir: {OUTPUT_FOLDER_PATH}")

    if not os.path.exists(REPLAY_FOLDER_PATH):
        print(f"Error: Input folder {REPLAY_FOLDER_PATH} does not exist.")
        return

    replay_files = [f for f in os.listdir(REPLAY_FOLDER_PATH) if f.lower().endswith(".sc2replay")]
    print(f"Found {len(replay_files)} replay files.\n")

    for filename in replay_files:
        full_path = os.path.join(REPLAY_FOLDER_PATH, filename)
        match_name = os.path.splitext(filename)[0]

        print(f"=== Processing: {match_name} ===")
        snapshots, real_winner_pid, real_winner_name = parse_replay_states(full_path)

        if not snapshots:
            print(f"Skipping {filename}: No snapshots.")
            continue

        print(f"Real Winner: {real_winner_name} (ID: {real_winner_pid})")

        for config in MODELS_CONFIG:
            try:
                process_single_match_with_model(snapshots, real_winner_pid, real_winner_name, match_name, config)
            except Exception as e:
                print(f"  [Fatal Error] Model {config['name']} interrupted: {e}")

        print("\n" + "-" * 30 + "\n")

    print(f"All tasks completed. Results in {OUTPUT_FOLDER_PATH}")


if __name__ == "__main__":
    main()