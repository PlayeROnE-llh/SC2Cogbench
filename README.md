<div align="center">

# <img src="assets/icon.png" width="30" height="30"> SC2-CogBench
### Benchmarking Cognitive Strategic Reasoning in Large Language Models through StarCraft II

[**Anonymous Authors**]



</div>

---

## 📖 Introduction

**SC2-CogBench** is the first cognitively grounded benchmark designed to evaluate the **Strategic Reasoning** capabilities of Large Language Models (LLMs) within the complex, adversarial environment of **StarCraft II**. 

[cite_start]Unlike prior works that focus on end-to-end outcome assessment (Win/Loss), SC2-CogBench decomposes strategic reasoning into a hierarchical cognitive process: **Perception**, **Prediction**, and **Strategy Inference**[cite: 61, 62].

<div align="center">
  <img src="assets/framework_v2.png" width="850"/>
  <br>
  [cite_start]<em>Figure 1: The hierarchical cognitive framework of SC2-CogBench, comprising 7 tasks across 3 dimensions[cite: 180].</em>
</div>

### 🌟 Key Features
* [cite_start]**Real-World Professional Data:** Curated from **174 Tier-S tournament matches** (EWC 2025, DreamHack), capturing authentic high-stakes decision-making[cite: 287].
* [cite_start]**Granular Diagnosis:** Features **7 distinct tasks** with **27 specialized metrics** to expose specific cognitive bottlenecks[cite: 196].
* [cite_start]**Expert Annotation:** A hybrid annotation protocol combining 7 human experts (Grandmaster level) and algorithmic grounding (XGBoost Win-Rate Models)[cite: 292, 293].

---

## 🏆 Leaderboard (SOTA Analysis)

[cite_start]We evaluated 6 frontier LLMs including **GPT-5**, **Gemini 3 Pro**, and **DeepSeek-V3**[cite: 484]. [cite_start]The results reveal that *no single model successfully completes the full perception-prediction-inference loop*[cite: 198].

| Dimensions | Task | Metric | 🥇 **GPT-5** | 🥈 **Gemini 3 Pro** | 🥉 **Claude 4 Sonnet** | **DeepSeek-V3** | **Qwen 3** |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Perception** | **KEI** | *F1-Score* | **0.480** | 0.197 | 0.260 | 0.347 | 0.347 |
| | **CSP** | *F1-Score* | 0.722 | 0.774 | 0.884 | **0.901** | 0.705 |
| | **BSS** | *Acc@120s* | 0.45 | 0.50 | 0.55 | 0.25 | **0.65** |
| **Prediction** | **DWP** | *Global Acc* | 0.46 | **0.62** | 0.48 | 0.50 | 0.54 |
| | **DWE** | *SSIS* | 70.05 | **79.39** | 71.42 | 49.60 | 44.40 |
| **Inference** | **ICD** | *EIY* | 6.3 | **18.8** | 10.7 | 6.0 | 7.5 |
| | **SAP** | *PSR* | **0.94** | 0.82 | 0.82 | 0.84 | 0.74 |

> [cite_start]**Analysis:** > - **Gemini 3 Pro** dominates in **Predictive Reasoning** (DWP/DWE) and **Intention Detection** (ICD), showing superior causal foresight[cite: 568, 571].
> [cite_start]- **GPT-5** excels in **Execution Compliance** (SAP) and **Event Identification** (KEI), acting as a "Conservative Expert"[cite: 566, 573].
> [cite_start]- **DeepSeek-V3** demonstrates robust **Perception Coverage** (CSP) but struggles with high-level strategic inference[cite: 498].

<div align="center">
  <img src="assets/radar_sota.png" width="600"/>
</div>

---

## 🧩 Task Taxonomy

SC2-CogBench includes 7 carefully designed tasks. Click below to expand definitions.

<details>
<summary><strong>👁️ Perception Layer (State Estimation)</strong></summary>

1. [cite_start]**Key Event Identification (KEI):** Filter raw logs to identify pivotal strategic moments (e.g., Tech Pivots, Decisive Engagements)[cite: 374].
2. [cite_start]**Battle Stage Segmentation (BSS):** Identify objective game phases (Early, Mid, Late) based on economic and tech thresholds[cite: 380].
3. [cite_start]**Conflict Spatiotemporal Perception (CSP):** Locate conflict events in both time and space from noisy telemetry[cite: 384].
</details>

<details>
<summary><strong>🔮 Prediction Layer (Value Function)</strong></summary>

4. [cite_start]**Dynamic Winner Prediction (DWP):** Predict the final winner based on a snapshot of the current state at fixed intervals[cite: 450].
5. [cite_start]**Dynamic Win-Rate Estimation (DWE):** Generate a continuous, real-time win-probability curve aligned with material reality[cite: 455].
</details>

<details>
<summary><strong>🧠 Strategy Inference Layer (Inverse Game Theory)</strong></summary>

6. [cite_start]**Intention Change Detection (ICD):** Reverse-engineer the opponent's latent intent shifts using the *Perception-Inference-Action* chain[cite: 466].
7. [cite_start]**Strategic Action Prediction (SAP):** Predict the next set of valid strategic actions (Units, Tech, Structure) under partial observability[cite: 471].
</details>

---

## 🛠️ Getting Started

### 1. Installation
```bash
git clone [https://github.com/YourRepo/SC2CogBench.git](https://github.com/YourRepo/SC2CogBench.git)
cd SC2CogBench
pip install -r requirements.txt
