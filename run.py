#!/usr/bin/env python3
"""Run the AgentGuard-FL experiments and write tables and figures to the results folder.

Examples:
    python run.py --dataset CICIoV2024=data/CICIoV2024
    python run.py --dataset CICIoV2024=data/CICIoV2024 --groups main models --seeds 42
    python run.py --synthetic --rounds 2 --seeds 42 --groups main
"""

import argparse
import os
import warnings
from dataclasses import replace

warnings.filterwarnings("ignore", category=FutureWarning)

from agentguard_fl.config import Config, pick_device
from agentguard_fl.data import (DATASET_SPECS, load_ids_dataset, prepare_dataset,
                                save_class_distribution, synthetic_dataset)
from agentguard_fl.experiments import ExperimentSettings, build_plan, run_plan, save_run_config
from agentguard_fl.reporting import final_rounds, save_figures, save_tables

GROUPS = ["main", "models", "ablation", "backbone", "heterogeneity", "sensitivity", "forged"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", action="append", default=[], metavar="NAME=PATH",
                   help=f"dataset to use; repeat for several. NAME is one of {list(DATASET_SPECS)}, "
                        "PATH is a CSV file or a folder of CSV files. With --synthetic, give NAME only.")
    p.add_argument("--synthetic", action="store_true",
                   help="use fake data to check the pipeline runs. Never report these results.")
    p.add_argument("--groups", nargs="+", choices=GROUPS, default=GROUPS, help="experiment groups to run")
    p.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    p.add_argument("--rounds", type=int, default=Config.n_rounds, help="communication rounds per run")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--device", default=None, help="cuda, mps or cpu (default: pick automatically)")
    p.add_argument("--no-figures", action="store_true")
    return p.parse_args()


def load_datasets(args: argparse.Namespace, cfg: Config) -> list:
    paths = dict(item.split("=", 1) if "=" in item else (item, None) for item in args.dataset)
    unknown = set(paths) - set(DATASET_SPECS)
    if unknown:
        raise SystemExit(f"Unknown dataset(s) {sorted(unknown)}; choose from {list(DATASET_SPECS)}.")
    if not paths and not args.synthetic:
        raise SystemExit("Give at least one --dataset NAME=PATH, or use --synthetic.")

    datasets = []
    # Dataset order is fixed: groups marked "first" use the first dataset selected here.
    for name, spec in DATASET_SPECS.items():
        if args.synthetic:
            if paths and name not in paths:
                continue
            print(f"[{name}] SYNTHETIC DEBUG DATA: do not report results from this.")
            X, y = synthetic_dataset(4000, 40, seed=len(datasets))
        elif name in paths:
            if not paths[name]:
                raise SystemExit(f"--dataset {name} needs a path: --dataset {name}=PATH")
            X, y = load_ids_dataset(name, paths[name], **spec)
        else:
            continue
        datasets.append(prepare_dataset(name, X, y, cfg))
    return datasets


def main() -> None:
    args = parse_args()
    device = args.device or pick_device()
    print("Device:", device)
    os.makedirs(args.results_dir, exist_ok=True)

    cfg = replace(Config(), n_rounds=args.rounds)
    defaults = ExperimentSettings()
    settings = replace(defaults, seeds=tuple(args.seeds),
                       run_groups={k: (v if k in args.groups else False) for k, v in defaults.run_groups.items()})

    datasets = load_datasets(args, cfg)
    save_class_distribution(datasets, os.path.join(args.results_dir, "test_class_distribution.csv"))

    plan = build_plan(datasets, cfg, settings)
    results = run_plan(plan, device, args.results_dir)
    save_run_config(os.path.join(args.results_dir, "config.txt"), cfg, settings)
    print("Results:", results.shape)

    final = final_rounds(results, args.results_dir)
    save_tables(final, args.results_dir)
    if not args.no_figures:
        save_figures(results, final, args.results_dir)


if __name__ == "__main__":
    main()
