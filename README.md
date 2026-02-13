<div align="center">

<img src="assets/icon.png" alt="SC2CogBench" width="100"/>

# SC2-CogBench
### Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II

[**Anonymous Authors**]



</div>

---

## 📖 Introduction

**SC2-CogBench** is the first cognitively grounded benchmark designed to rigorously evaluate the **Strategic Reasoning** capabilities of Large Language Models (LLMs) within the complex, adversarial environment of **StarCraft II**. 

[cite_start]Unlike existing benchmarks that focus on simple micro-management or end-to-end outcome assessment, SC2-CogBench leverages **174 professional Tier-S tournament matches** (EWC 2025, DreamHack) [cite: 63, 287] [cite_start]to decompose strategic reasoning into three hierarchical cognitive dimensions: **Perception**, **Prediction**, and **Strategy Inference**[cite: 62].

<div align="center">
  <img src="assets/framework.png" width="90%"/>
  <br>
  [cite_start]<em>Figure 1: The hierarchical framework of SC2-CogBench, covering 7 tasks and 27 granular metrics. [cite: 180]</em>
</div>

---

## 🏆 Comprehensive Leaderboard

[cite_start]We evaluated **6 frontier LLMs** (GPT-5, Gemini 3 Pro, Claude 4 Sonnet, DeepSeek-V3, Qwen 3, Kimi K2)[cite: 484]. [cite_start]The results reveal that **no single model successfully masters the full cognitive loop**[cite: 65, 198].

### 📊 Main Performance Matrix (Table 2)

| **Dimension** | **Task** | **Metric** | **GPT-5** | **Gemini 3 Pro** | **Claude 4 Sonnet** | **DeepSeek-V3** | **Qwen 3** | **Kimi K2** |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Perception** | **KEI** | *F1-Score* | **0.480** 🥇 | 0.197 | 0.260 | 0.347 | 0.347 | 0.350 |
| | **CSP** | *F1-Score* | 0.722 | 0.774 | 0.884 | **0.901** 🥇 | 0.705 | 0.370 |
| | **BSS** | *Acc@120s* | 0.45 | 0.50 | 0.55 | 0.25 | **0.65** 🥇 | 0.35 |
| **Prediction** | **DWP** | *Global Acc* | 0.46 | **0.62** 🥇 | 0.48 | 0.50 | 0.54 | 0.48 |
| | **DWE** | *SSIS* | 70.05 | **79.39** 🥇 | 71.42 | 49.60 | 44.40 | 61.12 |
| **Inference** | **ICD** | *EIY* | 6.25 | **18.80** 🥇 | 10.70 | 6.04 | 7.47 | 11.00 |
| | **SAP** | *PSR* | **0.94** 🥇 | 0.82 | 0.82 | 0.84 | 0.74 | 0.66 |

> **Metric Key:** **F1**: Harmonic mean of precision/recall; [cite_start]**SSIS**: Strategic Intelligence Score[cite: 1678]; [cite_start]**EIY**: Effective Inference Yield[cite: 1780]; [cite_start]**PSR**: Prediction Success Rate[cite: 1800].

---

## 🔬 Detailed Analysis & Conclusions

[cite_start]Our experiments uncover distinct "Strategic Personalities" among the models[cite: 725].

### 👁️ Perception Layer
* [cite_start]**Semantic Understanding:** **GPT-5** achieves state-of-the-art performance in **KEI** (0.480 F1), effectively filtering noise to identify semantic key events[cite: 566].
* [cite_start]**Combat Coverage:** **DeepSeek-V3** excels in **CSP** (0.901 F1), demonstrating superior sensitivity in tracking dense combat dynamics[cite: 498].
* [cite_start]**Temporal Structure:** **Qwen 3** shows the best temporal alignment in **BSS** (lowest error: 150.05s), maintaining a coherent rhythm of game phases[cite: 500].

### 🔮 Prediction Layer (The Foresight Gap)
* **Genuine Foresight:** **Gemini 3 Pro** is the only model demonstrating true strategic foresight. [cite_start]It dominates both **DWP** (0.62 Acc) and **DWE** (79.39 SSIS)[cite: 568].
* [cite_start]**Constraint:** Other models like Qwen 3 and Kimi K2 suffer from significant calibration errors ($WCE > 0.28$), relying on visible army count rather than causal reasoning[cite: 569].

### 🧠 Strategy Inference Layer
* [cite_start]**The "Broad Analyst":** **Gemini 3 Pro** achieves the highest **EIY** (18.8) in Intention Change Detection, effectively balancing the identification of interactive dynamics with validity[cite: 571].
* [cite_start]**The "Conservative Expert":** **GPT-5** leads in **SAP** (0.94 PSR), showing high adherence to valid build-order logic but remaining conservative in attribution[cite: 573].
* [cite_start]**Defensive Insight:** **Kimi K2** is the only model where *Loser Efficacy* > *Winner Efficacy*, indicating a specialized ability to understand defensive counter-play[cite: 2140].

<div align="center">
  <img src="assets/radar_chart.png" width="60%"/>
  <br>
  [cite_start]<em>Figure 2: Performance radar chart illustrating the heterogeneous capability profiles of the six LLMs. [cite: 182]</em>
</div>

---

## 🧩 Task Taxonomy

SC2-CogBench consists of 7 diverse tasks designed to test specific cognitive capabilities.

<details>
<summary><strong>Click to expand Task Definitions</strong></summary>

### 1. Perception
- [cite_start]**Key Event Identification (KEI):** Filter raw logs to extract pivotal moments (Strategic Inflection, Core Objective Impact)[cite: 374].
- [cite_start]**Battle Stage Segmentation (BSS):** Identify game phases (Early/Mid/Late) based on economic/tech thresholds[cite: 380].
- [cite_start]**Conflict Spatiotemporal Perception (CSP):** Locate conflict events in time and space[cite: 384].

### 2. Prediction
- [cite_start]**Dynamic Winner Prediction (DWP):** Binary prediction of the final winner from a static game state snapshot[cite: 450].
- [cite_start]**Dynamic Win-Rate Estimation (DWE):** Generate a continuous real-time win-probability curve[cite: 455].

### 3. Strategy Inference
- [cite_start]**Intention Change Detection (ICD):** Reverse-engineer latent intent shifts using the *Perception-Inference-Action* chain[cite: 466].
- [cite_start]**Strategic Action Prediction (SAP):** Predict valid strategic actions (Infrastructure, Tech, Units) in the next 90s window[cite: 471].
</details>

---

## 🛠️ Installation & Usage

### 1. Environment Setup
```bash
git clone [https://github.com/YourRepo/SC2CogBench.git](https://github.com/YourRepo/SC2CogBench.git)
cd SC2CogBench
conda create -n sc2bench python=3.10
conda activate sc2bench
pip install -r requirements.txt
