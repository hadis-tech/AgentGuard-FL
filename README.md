# AgentGuard-FL

Official implementation of:

AgentGuard-FL: A Robust Agentic Federated Intrusion Detection System Against Confidence-Aware Label-Flipping Attacks

Overview

AgentGuard-FL is a federated intrusion detection framework designed to defend against confidence-aware label-flipping attacks in Federated Learning environments.

Key Contributions
Confidence-Aware Label-Flipping Attack (CA-LFA)
Agentic client-side validation and label-consistency scoring
Reliability-weighted local training
Privacy-preserving telemetry
Trust-weighted server aggregation
Lightweight Tiny-BERT prompt-tuning architecture
Architecture

The proposed framework consists of:

CA-LFA attack module
Client-side AgentGuard controller
Trust-aware server aggregation
Privacy-preserving telemetry generation
Datasets

The experiments use:

N-BaIoT
CSE-CIC-IDS2018
CICIoV2024

Please download the datasets from their official sources and place them inside the datasets/ directory.

Installation
pip install -r requirements.txt
Running the Experiments

Open the notebook:

jupyter notebook AgentGuard_FL.ipynb

Run all cells sequentially.

Results

The notebook reproduces the experimental results reported in the paper, including:

Accuracy
Precision
Recall
F1-score
False Positive Rate (FPR)

under both:

Confidence-Aware Label-Flipping Attack (CA-LFA)
Random Label-Flipping Attack (RLFA)

Citation

License

This project is released under the MIT License.
