import json
import os
import sc2reader
from openai import OpenAI

# Configuration
MODELS_CONFIG = [
    {
        "name": "",
        "api_key": os.environ.get("DEEPSEEK_API_KEY", "YOUR_API_KEY_HERE"),
        "base_url": "",
        "model_id": "",
        "temperature": 0
    }
]


def extract_battle_events_from_replay(replay_path):
    try:
        replay = sc2reader.load_replay(replay_path)
        print(f"Successfully loaded replay file: {os.path.basename(replay_path)}")

        players = [p for p in replay.players if p.is_human]
        if len(players) < 2:
            print("Warning: Insufficient player data found")
            return []

        p1, p2 = players[0], players[1]
        print(f"Player 1: {p1.name}, Player 2: {p2.name}")

        death_events = []
        death_count = 0
        for event in replay.tracker_events:
            if event.name == "UnitDiedEvent":
                death_count += 1
                death_events.append({
                    "event_type": "death",
                    "second": int(event.second),
                    "dead_unit": event.unit.name if event.unit else "Unknown Unit",
                    "killer_unit": event.killing_unit.name if event.killing_unit else None,
                    "killer_player": event.killer.name if event.killer else None,
                    "x": event.x,
                    "y": event.y,
                    "data_basis": f"Unit death event: {event.unit.name if event.unit else 'Unknown Unit'}"
                })

        death_events.sort(key=lambda x: x["second"])

        # Save raw extraction for debugging
        debug_filename = f"extracted_events_{os.path.basename(replay_path).replace('.SC2Replay', '')}.json"
        with open(debug_filename, "w", encoding="utf-8") as f:
            json.dump(death_events, f, ensure_ascii=False, indent=2)

        return death_events

    except Exception as e:
        print(f"Error reading replay file: {e}")
        return []


def call_llm_for_csp(events_data, model_config):
    # PAPER PROMPT ALIGNMENT: CSP System Prompt
    system_prompt = (
        "Role: StarCraft II Battlefield Conflict Analyst.\n"
        "Task: Identify engagement windows and spatial regions from game telemetry.\n"
        "Definitions: Kinetic Frontier: Engagements breaching the Lethality-Volatility threshold. "
        "Tactical Lifecycle: The full duration including pre-conflict maneuvering and post-conflict disengagement."
    )

    # PAPER PROMPT ALIGNMENT: CSP User Prompt Structure
    user_prompt = f"""
Input Data: A sequence of unit death events from a StarCraft II match.
Data: {json.dumps(events_data[:500])} ... (truncated for context limit if necessary)

Task: Group these atomic events into distinct Conflict Episodes.
Format: start: [s], end: [s], region: [Coords], intensity: [Level]
Output Requirement: Return a JSON object with a key 'conflicts' containing a list of objects.
"""

    client = OpenAI(
        api_key=model_config['api_key'],
        base_url=model_config['base_url']
    )

    try:
        response = client.chat.completions.create(
            model=model_config['model_id'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=model_config['temperature']
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None


def main():
    REPLAY_FOLDER = "replays"
    if not os.path.exists(REPLAY_FOLDER):
        print(f"Folder {REPLAY_FOLDER} not found.")
        return

    replay_files = [f for f in os.listdir(REPLAY_FOLDER) if f.endswith(".SC2Replay")]

    for replay_file in replay_files:
        path = os.path.join(REPLAY_FOLDER, replay_file)
        events = extract_battle_events_from_replay(path)

        if not events: continue

        for config in MODELS_CONFIG:
            print(f"Running CSP analysis with {config['name']}...")
            result_text = call_llm_for_csp(events, config)

            if result_text:
                output_name = f"csp_{config['name']}_{replay_file}.json"
                with open(output_name, "w") as f:
                    f.write(result_text)
                print(f"Saved to {output_name}")


if __name__ == "__main__":
    main()