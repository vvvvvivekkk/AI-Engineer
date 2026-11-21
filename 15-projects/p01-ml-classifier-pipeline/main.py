"""
main.py - command-line entry point for Project 1.

Examples:
    python main.py                      # run all three datasets
    python main.py --dataset wine       # only the wine dataset
Outputs go to reports/: one markdown report and one confusion-matrix PNG per dataset.
"""
import argparse
import time
from pathlib import Path

from src.pipeline import LOADERS, run_experiment

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare classic classifiers in scikit-learn Pipelines")
    parser.add_argument("--dataset", choices=[*LOADERS, "all"], default="all")
    parser.add_argument("--out", default=str(HERE / "reports"), help="folder for reports and charts")
    args = parser.parse_args()

    names = list(LOADERS) if args.dataset == "all" else [args.dataset]
    for name in names:
        start = time.time()
        result = run_experiment(name, Path(args.out))
        # Print a short summary; the full details are in reports/report_<name>.md
        print(f"\n=== {name} ===")
        print(result["cv_table"].round(3).to_string(index=False))
        print(f"best: {result['best_model']} | test accuracy {result['test_accuracy']:.3f} "
              f"| test F1-macro {result['test_f1_macro']:.3f} | {time.time() - start:.1f}s")
    print(f"\nReports written to {args.out}")


if __name__ == "__main__":
    main()
