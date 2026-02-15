import os
import sys
import json
import re
from collections import Counter
from datetime import datetime
from openai import OpenAI
import sc2reader
from sc2reader.engine.plugins import SelectionTracker, APMTracker

MODELS_CONFIG = [
    {
        "name": "",
        "api_key": os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE"),
        "base_url": "",
        "model_id": "",
        "temperature": 0
    }
]

REPLAY_FOLDER = "replays"
OUTPUT_FOLDER = "./sap_results"
TIME_POINTS = [2.0, 4.0, 6.0, 8.0, 9.0]
PREDICTION_WINDOW_SECONDS = 90
NUM_SAMPLES = 5

VALID_ACTIONS = {
    "Terran": [
        "Barracks", "Factory", "Starport", "CommandCenter", "OrbitalCommand", "PlanetaryFortress",
        "EngineeringBay", "Armory", "FusionCore", "GhostAcademy", "Bunker", "MissileTurret",
        "TechLab", "Reactor", "Stimpack", "CombatShield", "InfernalPreigniter", "BansheeCloak", "YamatoGun",
        "SensorTower", "Refinery", "BarracksTechLab", "BarracksReactor", "FactoryTechLab", "FactoryReactor",
        "StarportTechLab", "StarportReactor", "ConcussiveShells", "DrillingClaws", "SmartServos",
        "CycloneLockOnDamageUpgrade", "HyperflightRotors", "AdvancedBallistics", "CorvidReactor",
        "CaduceusReactor", "PersonalCloaking", "EnhancedShockwaves", "TacNuke", "HiSecAutoTracking",
        "NeosteelArmor", "TerranInfantryWeapons", "TerranInfantryArmor", "TerranVehicleWeapons",
        "TerranVehicleAndShipPlating", "TerranShipWeapons"
    ],
    "Zerg": [
        "Hatchery", "Lair", "Hive", "SpawningPool", "RoachWarren", "BanelingNest", "HydraliskDen",
        "LurkerDen", "Spire", "GreaterSpire", "UltraliskCavern", "InfestationPit", "NydusNetwork",
        "EvolutionChamber", "SpineCrawler", "SporeCrawler", "ZerglingSpeed", "RoachSpeed", "BanelingSpeed",
        "HydraliskRange", "MutaliskAttack", "Extractor", "NydusWorm", "Burrow", "PneumatizedCarapace",
        "AdrenalGlands", "TunnelingClaws", "MuscularAugments", "GroovedSpines", "SeismicSpines",
        "AdaptiveTalons", "PathogenGlands", "NeuralParasite", "ChitinousPlating", "AnabolicSynthesis",
        "ZergMeleeWeapons", "ZergMissileWeapons", "ZergGroundArmor", "ZergFlyerWeapons", "ZergFlyerArmor"
    ],
    "Protoss": [
        "Nexus", "Gateway", "WarpGate", "CyberneticsCore", "RoboticsFacility", "RoboticsBay",
        "Stargate", "FleetBeacon", "TwilightCouncil", "TemplarArchives", "DarkShrine",
        "Forge", "PhotonCannon", "ShieldBattery", "WarpGateResearch", "Charge", "Blink", "PsionicStorm",
        "ExtendedThermalLance", "Pylon", "Assimilator", "ResonatingGlaives", "GraviticDrive",
        "GraviticBoosters", "AnionPulseCrystals", "PhoenixRange", "TectonicDestabilizers", "FluxVanes",
        "ShadowStride", "ProtossGroundWeapons", "ProtossGroundArmor", "ProtossShields", "ProtossAirWeapons",
        "ProtossAirArmor"
    ]
}

def clean_name(name):
    if not name: return None
    name = re.sub(r"^(Terran|Zerg|Protoss)", "", name)
    name = name.replace("Lowered", "").replace("Flying", "").replace("Research", "")
    invalid_keywords = ["MULE", "Larva", "Broodling", "SCV", "Probe", "Drone", "Egg", "AutoTurret", "KD8Charge"]
    if name in invalid_keywords: return None
    return name

def get_resources(replay, pid, frame):
    events = [e for e in replay.tracker_events if e.name == 'PlayerStatsEvent' and e.pid == pid and e.frame <= frame]
    if not events: return {"minerals": 0, "gas": 0, "supply": 0}
    latest = events[-1]
    return {
        "minerals": latest.minerals_current,
        "gas": latest.vespene_current,
        "supply": int(latest.food_used / 4096)
    }

def extract_full_game_context(replay_path, minute):
    sc2reader.engine.register_plugin(SelectionTracker())
    sc2reader.engine.register_plugin(APMTracker())

    try:
        replay = sc2reader.load_replay(replay_path, load_level=4)
    except Exception as e:
        print(f"   [SC2Reader Error]: {e}")
        return None

    target_frame = int(minute * 60 * 22.4)
    end_frame = target_frame + int(PREDICTION_WINDOW_SECONDS * 22.4)

    if target_frame > replay.frames:
        return None

    hero = replay.players[0]
    opponent = replay.players[1]

    resources = get_resources(replay, hero.pid, target_frame)

    current_buildings = set()
    current_army = []

    for unit in hero.units:
        if unit.started_at is not None and unit.started_at <= target_frame:
            if unit.died_at is None or unit.died_at > target_frame:
                c_name = clean_name(unit.name)
                if not c_name: continue
                if unit.is_building:
                    current_buildings.add(c_name)
                elif unit.is_army:
                    current_army.append(c_name)

    scouted_info = set()
    for unit in opponent.units:
        if unit.is_building and unit.started_at is not None and unit.started_at <= target_frame:
            c_name = clean_name(unit.name)
            if c_name and c_name not in ["SupplyDepot", "Pylon", "Overlord", "CreepTumor"]:
                scouted_info.add(c_name)

    ground_truth_actions = set()
    for event in replay.events:
        if event.frame < target_frame or event.frame > end_frame: continue
        if hasattr(event, 'control_pid') and event.control_pid != hero.pid: continue
        if hasattr(event, 'player') and event.player != hero: continue

        action = None
        if event.name == 'UnitInitEvent' or (event.name == 'UnitBornEvent' and event.unit.is_building):
            action = clean_name(event.unit.name)
        elif event.name == 'UnitTypeChangeEvent' and event.unit.owner == hero:
            action = clean_name(event.unit_type_name)
        elif event.name == 'UpgradeCompleteEvent':
            if event.frame <= (end_frame + 2000):
                action = clean_name(event.upgrade_type_name)

        if action and action not in ["SupplyDepot", "Pylon", "Overlord", "CreepTumor", "Refinery", "Extractor", "Assimilator"]:
            ground_truth_actions.add(action)

    return {
        "race": hero.play_race,
        "opponent_race": opponent.play_race,
        "time_min": minute,
        "minerals": resources['minerals'],
        "gas": resources['gas'],
        "supply": resources['supply'],
        "my_army_composition": dict(Counter(current_army)),
        "my_tech_structure": list(current_buildings),
        "scouted_opponent": list(scouted_info),
        "ground_truth": list(ground_truth_actions) if ground_truth_actions else ["None"]
    }

def generate_data_driven_prompt(data):
    valid_list = VALID_ACTIONS.get(data['race'], [])
    valid_str = ", ".join(valid_list)

    army_str = ", ".join([f"{k}: {v}" for k, v in data['my_army_composition'].items()]) or "None"
    tech_str = ", ".join(data['my_tech_structure']) or "Base Structure Only"
    scouted_str = ", ".join(data['scouted_opponent']) or "No Intel"

    # PAPER PROMPT ALIGNMENT: SAP User Input
    prompt = f"""
Current Game State:
- Time: {data['time_min']} minutes
- Matchup: {data['race']} vs {data['opponent_race']}
- Resources: Minerals: {data['minerals']}, Gas: {data['gas']}, Supply: {data['supply']}
- Active Army: [{army_str}]
- Completed Infrastructure: [{tech_str}]
- Known Enemy Structures: [{scouted_str}]

Task: Forecast a set of valid strategic actions within a subsequent 90-second window.
Definitions: Policy Coherence: Balancing economic and military demands via build order schemas.
Whitelist Domains: Categorized actions: Infrastructure, Tech, Units, and Upgrades.
Format: time: [s], predicted_actions: [List], category: [Domain]

Constraints:
- Select actions ONLY from: [{valid_str}]
- Return strictly valid JSON with key "predictions".
"""
    return prompt

def calculate_advanced_stats(ground_truth_list, all_samples_preds):
    gt_set = set(ground_truth_list)
    if "None" in gt_set: gt_set.remove("None")

    action_hit_counts = {action: 0 for action in gt_set}
    total_predictions_made = 0
    total_correct_predictions = 0

    for sample_preds in all_samples_preds:
        s_preds = set(sample_preds)
        total_predictions_made += len(s_preds)
        intersect = gt_set.intersection(s_preds)
        total_correct_predictions += len(intersect)
        for hit_action in intersect:
            action_hit_counts[hit_action] += 1

    high_conf_hits = [k for k, v in action_hit_counts.items() if v > (NUM_SAMPLES / 2)]
    low_conf_hits = [k for k, v in action_hit_counts.items() if 0 < v <= (NUM_SAMPLES / 2)]
    missed_actions = [k for k, v in action_hit_counts.items() if v == 0]
    precision = (total_correct_predictions / total_predictions_made) if total_predictions_made > 0 else 0.0

    return {
        "action_hit_details": action_hit_counts,
        "high_confidence_hits": high_conf_hits,
        "low_confidence_hits": low_conf_hits,
        "missed_actions": missed_actions,
        "prediction_precision": precision,
        "total_predictions_made": total_predictions_made,
        "total_correct_predictions": total_correct_predictions
    }

def run_single_experiment(replay_path, model_config):
    replay_filename = os.path.basename(replay_path)
    model_name = model_config['name']
    output_filename = f"{model_name}_{replay_filename.replace('.SC2Replay', '')}.json"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    if os.path.exists(output_path):
        print(f"   [Skip] Result already exists: {output_filename}")
        return

    print(f"\n   >>> Model: {model_name} | Replay: {replay_filename}")

    full_log = {
        "experiment_meta": {
            "model_name": model_name,
            "replay_file": replay_filename,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "timepoints_results": [],
        "global_summary": {}
    }

    client = OpenAI(api_key=model_config['api_key'], base_url=model_config['base_url'])
    global_hits = 0
    global_samples = 0

    # PAPER PROMPT ALIGNMENT: SAP System Prompt
    system_prompt = (
        "Role: StarCraft II Macro-management Logic Planner.\n"
        "Task: Forecast a set of valid strategic actions within a subsequent 90-second window."
    )

    for minute in TIME_POINTS:
        print(f"       Timepoint: {minute}m", end="", flush=True)

        data = extract_full_game_context(replay_path, minute)
        if data is None:
            print(" -> Skipped (No Data)")
            full_log["timepoints_results"].append({"time_min": minute, "status": "Skipped"})
            continue

        prompt = generate_data_driven_prompt(data)
        gt_normalized = [str(x).lower().replace(" ", "") for x in data['ground_truth']]
        gt_set = set(gt_normalized)

        timepoint_log = {
            "time_min": minute,
            "status": "Success",
            "ground_truth": gt_normalized,
            "extracted_data": data,
            "prompt": prompt,
            "samples": []
        }

        all_samples_preds_list = []

        for i in range(NUM_SAMPLES):
            try:
                resp = client.chat.completions.create(
                    model=model_config['model_id'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=model_config['temperature']
                )
                raw_text = resp.choices[0].message.content
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                json_str = match.group(0) if match else raw_text
                res_json = json.loads(json_str)
                preds = [str(p).lower().replace(" ", "") for p in res_json.get("predictions", [])]
                analysis = res_json.get("analysis", "N/A")

                all_samples_preds_list.append(preds)
                is_hit = len(gt_set.intersection(set(preds))) > 0

                timepoint_log["samples"].append({
                    "id": i + 1,
                    "raw_response": raw_text,
                    "predictions": preds,
                    "analysis": analysis,
                    "is_hit": is_hit
                })
            except Exception as e:
                timepoint_log["samples"].append({"id": i + 1, "error": str(e)})

        advanced_stats = calculate_advanced_stats(gt_normalized, all_samples_preds_list)
        timepoint_log["advanced_analysis"] = advanced_stats

        valid_samples = [s for s in timepoint_log["samples"] if "is_hit" in s]
        hit_count = sum(1 for s in valid_samples if s["is_hit"])
        pass_rate = (hit_count / len(valid_samples) * 100) if valid_samples else 0
        timepoint_log["pass_rate_percent"] = pass_rate

        full_log["timepoints_results"].append(timepoint_log)
        global_hits += hit_count
        global_samples += len(valid_samples)

        print(f" -> Done. Pass Rate: {pass_rate:.0f}%")

    global_accuracy = (global_hits / global_samples * 100) if global_samples > 0 else 0
    full_log["global_summary"] = {
        "total_samples": global_samples,
        "total_hits": global_hits,
        "overall_accuracy": global_accuracy
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_log, f, indent=4, ensure_ascii=False)
    print(f"   Saved to {output_filename}")

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output directory: {OUTPUT_FOLDER}")

    if not os.path.exists(REPLAY_FOLDER):
        print(f"Error: Replay folder '{REPLAY_FOLDER}' does not exist.")
        return

    replay_files = [f for f in os.listdir(REPLAY_FOLDER) if f.endswith(".SC2Replay")]

    if not replay_files:
        print(f"No .SC2Replay files found in {REPLAY_FOLDER}")
        return

    print(f"Found {len(replay_files)} replays. Models to test: {len(MODELS_CONFIG)}")

    for replay_file in replay_files:
        replay_path = os.path.join(REPLAY_FOLDER, replay_file)
        for model_config in MODELS_CONFIG:
            try:
                run_single_experiment(replay_path, model_config)
            except Exception as e:
                print(f"Critical Error running {model_config['name']} on {replay_file}: {e}")
                continue

    print("\nAll experiments completed!")

if __name__ == "__main__":
    main()