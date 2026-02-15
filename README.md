<div align="center">

# SC2-CogBench
### Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II

</div>

---

## 📖 Introduction

**SC2-CogBench** is a cognitively motivated benchmark designed to evaluate **Strategic Reasoning** in Large Language Models (LLMs) within the complex, adversarial environment of **StarCraft II**.

Unlike existing benchmarks that focus on simple micro-management or end-to-end outcome assessment, SC2-CogBench leverages **174 professional Tier-S tournament matches** (EWC 2025, DreamHack). It decomposes strategic reasoning into three hierarchical cognitive dimensions: **Perception**, **Prediction**, and **Strategy Inference**.

### 🧩 The Framework
SC2-CogBench employs **27 task-specific metrics** to capture diverse cognitive demands across the perception-prediction-inference loop.

<div align="center">
  <img src="Figures/Figure1_Framework.png" alt="Figure 1: Hierarchical Framework" width="100%"/>
  <br>
  <em>Figure 1: The hierarchical framework of SC2-CogBench, organized into Perception, Prediction, and Strategy Inference.</em>
</div>

---

## 🏗️ Data Construction

The dataset captures the authentic, high-stakes adversarial dynamics of elite human competition. We constructed **150 evaluation instances** with semantically grounded human expert annotations.

* **Source:** 174 raw matches from 2025 Tier-S Tournaments (EWC & DreamHack).
* **Annotation:** A hybrid protocol involving 7 human experts and an XGBoost-based Win-Rate Model for objective grounding.

<div align="center">
  <img src="Figures/Figure3_Pipeline.png" alt="Figure 3: Data Pipeline" width="100%"/>
  <br>
  <em>Figure 3: SC2-CogBench is constructed from the latest 2025 match data, filtered and annotated by experts.</em>
</div>

---

## 🏆 Leaderboard & Experimental Results

We evaluated 6 frontier LLMs: **GPT-5**, **Gemini 3 Pro**, **Claude 4 Sonnet**, **DeepSeek-V3**, **Qwen 3**, and **Kimi K2**.

### 🧠 Capability Overview
Evaluations reveal a highly heterogeneous capability profile. No single model successfully completes the full reasoning loop.

<div align="center">
  <img src="Figures/Figure2_Results.png" alt="Figure 2: Radar Chart" width="80%"/>
  <br>
  <em>Figure 2: Experimental results of six LLMs across Perception, Prediction, and Strategy Inference tasks.</em>
</div>

### 🥇 Summary Scores
*A high-level comparison of the best performing models across tasks (derived from Table 2).*

| Task | Metric | GPT-5 | Gemini-3 | Claude-4 | DeepSeek-V3 | Qwen-3 | Kimi-K2 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **KEI** | *F1-Score* | **0.480** | 0.197 | 0.260 | 0.347 | 0.347 | 0.350 |
| **CSP** | *F1-Score* | 75.22 | 83.58 | **88.64** | 87.00 | 67.88 | 38.18 |
| **BSS** | *Accuracy* | 45 | 50 | **55** | 25 | **65** | 35 |
| **DWP** | *Accuracy* | 49.15 | **66.05** | 52.95 | 53.00 | 49.35 | 40.20 |
| **DWE** | *SSIS* | 70.05 | **79.39** | 71.42 | 49.60 | 44.40 | 61.12 |
| **ICD** | *EIY* | 6.25 | **18.80** | 10.70 | 6.04 | 7.47 | 11.00 |
| **SAP** | *PSR* | **66.64** | 61.60 | 56.32 | 57.72 | 49.88 | 43.92 |

---

### 📊 Detailed Benchmarking (Full Metrics)

Below is the complete breakdown of all **27 metrics** across the three cognitive dimensions.

#### 1. Perception Layer
*Evaluates situational awareness and state abstraction.*

| Task | Metric | GPT-5 | Gemini-3 | Claude-4 | DeepSeek-V3 | Qwen-3 | Kimi-K2 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **KEI** | Precision | **0.405** | 0.157 | 0.362 | 0.324 | 0.260 | 0.366 |
| | Recall | 0.728 | **0.738** | 0.220 | 0.552 | 0.551 | 0.353 |
| | F1-Score | **0.480** | 0.197 | 0.260 | 0.347 | 0.347 | 0.350 |
| | Redundancy $\downarrow$ | **0.595** | 0.842 | 0.638 | 0.676 | 0.740 | 0.635 |
| | ATE $\downarrow$ | 2.7 | 3.4 | **2.1** | 3.1 | 5.9 | 4.1 |
| **BSS** | AbsErr $\downarrow$ | 182.90 | 179.65 | 256.85 | 210.55 | **150.05** | 196.30 |
| | SDRE $\downarrow$ | 0.63 | **0.59** | 0.84 | 0.71 | 0.60 | 0.62 |
| | OSC $\downarrow$ | 1 | 2 | 4 | **0** | 1 | 2 |
| | Acc@30 | 0 | **0.25** | 0.20 | 0.15 | 0.15 | 0 |
| | Acc@60 | 0.5 | 0.25 | **0.35** | 0.15 | 0.30 | 0.15 |
| | Acc@120 | 0.45 | 0.50 | 0.55 | 0.25 | **0.65** | 0.35 |
| | T-Bias $\downarrow$ | **-62.85** | -94.75 | -225.3 | -202.7 | -134.5 | -188.5 |
| **CSP** | Precision | **0.948** | 0.878 | 0.917 | 0.873 | 0.803 | 0.303 |
| | Recall | 0.583 | 0.692 | 0.853 | **0.929** | 0.628 | 0.474 |
| | F1-Score | 0.722 | 0.774 | 0.884 | **0.901** | 0.705 | 0.370 |
| | TPC | 0.801 | **0.942** | 0.897 | 0.835 | 0.658 | 0.412 |
| | SPC | 0.794 | **0.915** | 0.883 | 0.812 | 0.621 | 0.387 |

#### 2. Prediction Layer
*Assess the capacity for forward-looking reasoning and outcome forecasting.*

| Task | Metric | GPT-5 | Gemini-3 | Claude-4 | DeepSeek-V3 | Qwen-3 | Kimi-K2 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DWP** | Acct=2 | 0.40 | **0.60** | 0.30 | 0.40 | 0.50 | 0.20 |
| | Acct=4 | 0.50 | **0.60** | 0.40 | 0.50 | 0.20 | 0.30 |
| | Acct=6 | 0.40 | **0.70** | 0.60 | 0.40 | 0.60 | 0.50 |
| | Acct=8 | 0.50 | 0.70 | 0.70 | 0.60 | 0.80 | **1.00** |
| | Acct=10 | 0.50 | 0.50 | 0.40 | **0.60** | **0.60** | 0.40 |
| | EGF | 0.45 | **0.60** | 0.35 | 0.45 | 0.35 | 0.25 |
| | LGR | 0.50 | 0.60 | 0.55 | 0.60 | **0.70** | **0.70** |
| | PSS | 0.575 | **0.775** | **0.775** | 0.650 | 0.575 | 0.450 |
| | Global Acc | 0.46 | **0.62** | 0.48 | 0.50 | 0.54 | 0.48 |
| **DWE** | **SSIS** | 70.05 | **79.39** | 71.42 | 49.60 | 44.40 | 61.12 |
| | ZA | 0.584 | **0.806** | 0.619 | 0.354 | 0.360 | 0.544 |
| | FA | **0.90** | **0.90** | **0.90** | 0.60 | 0.50 | 0.70 |
| | BAS $\downarrow$ | 0.155 | **0.131** | 0.152 | 0.211 | 0.233 | 0.167 |
| | WCE $\downarrow$ | 0.242 | **0.214** | 0.240 | 0.286 | 0.312 | 0.247 |

#### 3. Strategy Inference Layer
*Reasoning about latent intent and policy selection.*

| Task | Metric | GPT-5 | Gemini-3 | Claude-4 | DeepSeek-V3 | Qwen-3 | Kimi-K2 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ICD** | GTR | 0.33 | 0.64 | 0.58 | 0.43 | **0.78** | 0.52 |
| | WinEff | **0.66** | 0.46 | 0.54 | 0.45 | 0.42 | 0.45 |
| | LoseEff | **0.59** | 0.48 | 0.53 | 0.42 | 0.44 | 0.50 |
| | **EIY** $\uparrow$ | 6.25 | **18.8** | 10.7 | 6.04 | 7.47 | 11.00 |
| **SAP** | F1-Score | **0.242** | 0.220 | 0.196 | 0.201 | 0.169 | 0.146 |
| | Precision | **0.273** | 0.254 | 0.222 | 0.235 | 0.198 | 0.160 |
| | Recall | **0.219** | 0.195 | 0.177 | 0.178 | 0.151 | 0.135 |
| | **PSR** | **0.94** | 0.88 | 0.82 | 0.84 | 0.74 | 0.66 |

---

## 🖊️ Citation

If you use SC2-CogBench in your research, please cite our paper:

```bibtex
@inproceedings{sc2cogbench2026,
  title={SC2-CogBench: Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II},
  author={Anonymous Authors},
  booktitle={Under Review},
  year={2026}
}
