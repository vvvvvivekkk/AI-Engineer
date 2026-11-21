"""
main.py - trains an MLP and a CNN on 8x8 digits and writes charts to reports/.

    python main.py                       # both models, early stopping
    python main.py --model cnn --augment # CNN with data augmentation
    python main.py --epochs 5            # quick smoke test
"""
import argparse
import json
import time
from pathlib import Path

import torch

from src.data import load_arrays, loader, split
from src.evaluate import plot_confusion, plot_curves, plot_filters, plot_misclassified
from src.models import MLP, SmallCNN, count_params
from src.train import fit, predict

HERE = Path(__file__).resolve().parent
torch.set_num_threads(2)  # be polite on small/shared machines


def main() -> None:
    ap = argparse.ArgumentParser(description="MLP vs CNN on 8x8 handwritten digits")
    ap.add_argument("--model", choices=["mlp", "cnn", "both"], default="both")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--augment", action="store_true", help="random 1-pixel shifts + noise while training")
    ap.add_argument("--out", default=str(HERE / "reports"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (HERE / "models").mkdir(exist_ok=True)

    images, labels = load_arrays()
    (x_tr, y_tr), (x_val, y_val), (x_te, y_te) = split(images, labels)
    print(f"train {len(y_tr)} | validation {len(y_val)} | test {len(y_te)} images")
    train_dl = loader(x_tr, y_tr, shuffle=True)
    val_dl = loader(x_val, y_val)

    names = ["mlp", "cnn"] if args.model == "both" else [args.model]
    histories, summary = {}, {}
    for name in names:
        torch.manual_seed(0)                      # same starting weights every run
        model = MLP() if name == "mlp" else SmallCNN()
        start = time.time()
        model, hist = fit(model, train_dl, val_dl, epochs=args.epochs,
                          patience=args.patience, use_augment=args.augment)
        pred = predict(model, torch.from_numpy(x_te)).numpy()
        acc = float((pred == y_te).mean())
        histories[name] = hist
        plot_confusion(y_te, pred, f"{name.upper()} - test accuracy {acc:.3f}", out / f"confusion_{name}.png")
        n_wrong = plot_misclassified(x_te, y_te, pred, out / f"misclassified_{name}.png")
        if name == "cnn":
            plot_filters(model, out / "cnn_filters.png")
        torch.save(model.state_dict(), HERE / "models" / f"{name}.pt")
        summary[name] = {"test_accuracy": round(acc, 4), "wrong": n_wrong, "params": count_params(model),
                         "epochs_run": hist["epochs_run"], "best_epoch": hist["best_epoch"],
                         "seconds": round(time.time() - start, 1), "augment": args.augment}
        print(f"{name.upper():4s} test accuracy {acc:.3f} | {n_wrong} wrong | "
              f"{summary[name]['params']:,} params | stopped after {hist['epochs_run']} epochs "
              f"(best {hist['best_epoch']}) | {summary[name]['seconds']}s")

    plot_curves(histories, out / "loss_curves.png")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"charts + summary.json written to {out}")


if __name__ == "__main__":
    main()
