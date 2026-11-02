# AgentGuard-FL

Code for *AgentGuard-FL: A Robust Agentic Federated Intrusion Detection System Against
Confidence-Aware Label-Flipping Attacks*. Equation, algorithm and table numbers in the code
comments refer to the paper.

AgentGuard-FL trains a BERT-Tiny intrusion detector across clients. Each honest client runs an
agent that down-weights suspicious labels and clips its update, and the server weights clients by
trust and reputation. The code compares this against FedAvg, Krum and Trimmed Mean under
label-flipping (CA-LFA, RLFA) and model-poisoning (ALIE) attacks.

## Install

Python 3.9 or later.

```bash
git clone <repository-url>
cd agentguard-fl
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run downloads `prajjwal1/bert-tiny` from Hugging Face.

## Data

The datasets are not included. Download them from their publishers and put the CSV files in a
folder of your choice:

| Name | Source |
|---|---|
| `N-BaIoT` | UCI Machine Learning Repository (label comes from the file path: paths containing `benign` are normal) |
| `CSE-CIC-IDS2018` | Canadian Institute for Cybersecurity |
| `CICIoV2024` | Canadian Institute for Cybersecurity |

Labels are binary (0 = normal, 1 = attack). Sampling is set per dataset in `DATASET_SPECS` in
`agentguard_fl/data.py`, and duplicate rows are removed. To look at a CICIoV2024 folder first, run
`python scripts/inspect_dataset.py data/CICIoV2024`.

## Run

Check that everything works, using fake data (results mean nothing):

```bash
python run.py --synthetic --dataset N-BaIoT --rounds 2 --seeds 42 --groups main
```

Run the full experiment plan on real data:

```bash
python run.py \
  --dataset N-BaIoT=data/N-BaIoT \
  --dataset CSE-CIC-IDS2018=data/CSE-CIC-IDS2018 \
  --dataset CICIoV2024=data/CICIoV2024
```

Options: `--groups`, `--seeds`, `--rounds`, `--results-dir`, `--device`, `--no-figures`. See
`python run.py --help`. Model and attack parameters are in `agentguard_fl/config.py`, and attack
rates and the experiment grid are in `agentguard_fl/experiments.py`.

**Long runs.** Results are saved to `results/all_rounds.csv` after every run, and running the same
command again skips finished runs. Delete `results/` after changing the configuration.

## Experiments

| Group | What it does | Output in `results/` |
|---|---|---|
| `main` | AgentGuard-FL, FedAvg, Krum and Trimmed Mean under no attack, CA-LFA, RLFA and ALIE | `table_main.csv`, `accuracy_*.png`, `cm_*.png` |
| `models` | FedRNN, FedCNN and FedLSTM under each attack | `table_models.csv` |
| `ablation` | Each client component and each trust term switched off in turn | `table_ablation.csv` |
| `backbone` | Random frozen BERT, BERT trained from scratch and MLP in the same pipeline | `table_backbone.csv` |
| `heterogeneity` | IID and Dirichlet α sweep | `table_heterogeneity.csv` |
| `sensitivity` | Sweeps over κ_q, λ_R, γ_q and τ | `table_sensitivity.csv` |
| `forged` | Attackers report perfect telemetry | `table_forged_telemetry.csv` |

Every run also writes:

- `all_rounds.csv`: every round of every run
- `per_run_final.csv`: each seed's final counts and metrics
- `test_class_distribution.csv`: class counts per split
- `config.txt`: the configuration used

Tables are also written as LaTeX (`.tex`). `heterogeneity` and `sensitivity` use the first dataset
selected; the other groups use all of them.

All metrics come from one confusion matrix on one fixed test set, with attack as the positive
class. Tables report mean ± std over seeds, with the 95% confidence interval in the CSV.

## Threat model

The threat model is the same for every defence. Malicious clients control their own data and
training. Label-flipping attackers poison their labels and run Algorithm 1 of the paper; the ALIE
attacker trains honestly and then submits a crafted update. Attackers never run the AgentGuard
agent. By default they report telemetry computed honestly from their own data; with
`attacker_forges_telemetry=True` they report perfect telemetry. The server measures the update norm
from the received update, so it cannot be faked.

Krum needs n > 2f + 2, which 4 attackers of 10 clients does not satisfy, so the defender's f is
capped at 3 for Krum.

The FedRNN, FedCNN and FedLSTM models are simple sequence baselines implemented in
`agentguard_fl/models.py`.

## Layout

```
run.py                     command-line entry point
agentguard_fl/
    config.py              all parameters
    data.py                loading, splitting, tokenisation
    models.py              BERT-Tiny model and baselines
    attacks.py             CA-LFA, RLFA, ALIE
    client.py              local training and the client agent
    server.py              AgentGuard-FL, FedAvg, Krum, Trimmed Mean
    metrics.py             metrics from the confusion matrix
    federation.py          partitioning and the training loop
    experiments.py         experiment plan and resumable runner
    reporting.py           tables and figures
scripts/inspect_dataset.py dataset summary
```
