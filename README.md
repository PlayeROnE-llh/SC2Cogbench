# SC2-CogBench: Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II

<div align="center">

[![Paper](https://img.shields.io/badge/Paper-Arxiv-red)](https://arxiv.org/abs/2026.xxxxx) 
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow)](https://huggingface.co/datasets/YourOrg/SC2CogBench)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-blue)](LICENSE)

[**Introduction**](#-introduction) | [**Leaderboard**](#-leaderboard) | [**Dataset**](#-dataset) | [**Evaluation**](#-evaluation) | [**Citation**](#-citation)

</div>

---

## 📢 News
* **[2026-02-12]** We released the **SC2-CogBench** paper and dataset! Code is now available.

## 📖 Introduction

**SC2-CogBench** is the first cognitively grounded benchmark designed to evaluate **Strategic Reasoning** in Large Language Models (LLMs) using the complex adversarial environment of **StarCraft II**. 

Unlike existing benchmarks that focus on end-to-end win rates or simple micro-management, SC2-CogBench decomposes strategic reasoning into three hierarchical cognitive dimensions: **Perception**, **Prediction**, and **Strategy Inference**.

<div align="center">
  <img src="assets/framework.png" width="800"/>
  <br>
  <em>Figure 1: The hierarchical framework of SC2-CogBench.</em>
</div>

### Key Features
* **Real-World Professional Data:** Constructed from 174 Tier-S tournament matches (EWC 2025, DreamHack) with 150 high-quality expert-annotated instances.
* **Cognitive Hierarchy:** Covers 7 distinct tasks ranging from *Key Event Identification* (KEI) to *Intention Change Detection* (ICD).
* **Rigorous Metrics:** 27 task-specific metrics including *Effective Inference Yield* (EIY) and *Strategic Intelligence Score* (SSIS).

---

## 🏆 Leaderboard

We evaluated 6 frontier LLMs (including GPT-5, Gemini 3 Pro, Claude 4 Sonnet, DeepSeek-V3). Below is the summary performance across three dimensions.

| Model | **KEI** (F1) | **CSP** (F1) | **BSS** (Acc) | **DWP** (Acc) | **DWE** (SSIS) | **ICD** (EIY) | **SAP** (PSR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPT-5** | **0.480** | 0.722 | 0.45 | 0.46 | 70.05 | 6.25 | **0.94** |
| **Gemini 3 Pro** | 0.197 | 0.774 | 0.50 | **0.62** | **79.39** | **18.80** | 0.82 |
| **Claude 4 Sonnet** | 0.260 | 0.884 | 0.55 | 0.48 | 71.42 | 10.70 | 0.88 |
| **DeepSeek-V3** | 0.347 | **0.901** | 0.25 | 0.50 | 49.60 | 6.04 | 0.84 |
| **Qwen 3** | 0.347 | 0.705 | **0.65** | 0.54 | 44.40 | 7.47 | 0.74 |
| **Kimi K2** | 0.350 | 0.370 | 0.35 | 0.48 | 61.12 | 11.00 | 0.66 |

> **Analysis:** No single model masters the full loop. **Gemini 3 Pro** excels in predictive foresight (DWP/DWE), while **GPT-5** dominates in structured strategic adherence (SAP) and key event identification (KEI).

---

## 📂 Dataset

The dataset is derived from `.SC2Replay` files processed into structured JSON logs.

### Data Structure
```json
{
  "match_id": "EWC2025_Serral_vs_Cure",
  "duration": 1340,
  "events": [
    {"time": 120, "type": "UnitBorn", "unit": "Queen", "pos": [32, 45]},
    ...
  ],
  "annotations": {
    "kei": [...],
    "bss_transitions": [300, 850],
    "winner": "Zerg"
  }
}
```

### Download
Please download the full dataset from [HuggingFace](https://huggingface.co/datasets/YourOrg/SC2CogBench) and extract it to the `./data` folder.

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YourUsername/SC2CogBench.git](https://github.com/YourUsername/SC2CogBench.git)
   cd SC2CogBench
   ```

2. **Install dependencies**
   ```bash
   conda create -n sc2bench python=3.10
   conda activate sc2bench
   pip install -r requirements.txt
   ```
   *Note: We strictly use `sc2reader` for parsing replay files.*

---

## 🚀 Evaluation

We provide scripts to evaluate models on all 7 tasks.

### 1. Configure API Keys
Create a `.env` file and add your model API keys:
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant...
```

### 2. Run Perception Tasks (KEI, BSS, CSP)
```bash
python -m sc2cogbench.evaluate \
    --task KEI \
    --model gpt-5 \
    --data_path ./data/test_set.json \
    --output_dir ./results
```

### 3. Run Strategy Inference Tasks (ICD, SAP)
```bash
python -m sc2cogbench.evaluate \
    --task SAP \
    --model gemini-3-pro \
    --cot True \  # Enable Chain-of-Thought
    --output_dir ./results
```

---

## 📝 Tasks Overview

SC2-CogBench consists of 7 tasks across 3 dimensions:

1.  **Perception Layer**
    * **KEI (Key Event Identification):** Identify pivotal moments (e.g., tech switches, decisive battles).
    * **BSS (Battle Stage Segmentation):** Segment game into Early/Mid/Late phases.
    * **CSP (Conflict Spatiotemporal Perception):** Locate battles in space and time.

2.  **Prediction Layer**
    * **DWP (Dynamic Winner Prediction):** Predict the winner at fixed intervals (2, 4, 6 min...).
    * **DWE (Dynamic Win-Rate Estimation):** Generate a real-time win-probability curve.

3.  **Strategy Inference Layer**
    * **ICD (Intention Change Detection):** Detect shifts in player strategy (e.g., from defensive to aggressive).
    * **SAP (Strategic Action Prediction):** Predict the next set of strategic actions (tech/units) given the current state.

---

## 🖊️ Citation

If you find this work useful, please cite our paper:

```bibtex
@inproceedings{sc2cogbench2026,
  title={SC2-CogBench: Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II},
  author={Anonymous Authors},
  booktitle={Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year={2026}
}
```

## 📄 License

This project is licensed under the [CC BY-NC 4.0](LICENSE) License. Game data remains the property of Blizzard Entertainment.
