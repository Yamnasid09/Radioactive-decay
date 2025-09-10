import argparse, os, json
import numpy as np
import matplotlib.pyplot as plt

def load_series(run_dir: str):
    t = np.load(os.path.join(run_dir, "t.npy"))
    mean = None
    std = None

    traj_p = os.path.join(run_dir, "traj.npy")
    if os.path.exists(traj_p):
        traj = np.load(traj_p).astype(float)   # shape: (R, T)
        mean = traj.mean(axis=0)
        std  = traj.std(axis=0, ddof=0)
    else:
        n_p = os.path.join(run_dir, "N.npy")
        if os.path.exists(n_p):
            mean = np.load(n_p).astype(float)
            std  = np.zeros_like(mean)
        else:
            raise SystemExit("traj.npy or N.npy not found in run dir.")

    meta = {}
    mpath = os.path.join(run_dir, "meta.json")
    if os.path.exists(mpath):
        with open(mpath) as f:
            meta = json.load(f)
    return t, mean, std, meta

def main():
    ap = argparse.ArgumentParser(description="Plot mean ± std band from a saved MC run")
    ap.add_argument("--run-dir", default="data/runs/last")
    ap.add_argument("--out", default="images")
    ap.add_argument("--alpha", type=float, default=0.25)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    t, mu, sd, meta = load_series(args.run_dir)

    plt.figure()
    plt.plot(t, mu, label="mean N(t)")
    if np.any(sd > 0):
        lo, hi = mu - sd, mu + sd
        plt.fill_between(t, lo, hi, alpha=args.alpha, label="±1σ")
    plt.xlabel("Time"); plt.ylabel("Counts")
    ttl = f"Ensemble mean ± std — {meta.get('mode','')}".strip(" -")
    plt.title(ttl); plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
    outp = os.path.join(args.out, "nt_curve_band.png")
    plt.savefig(outp, dpi=200)
    print(f"[OK] Saved {outp}")

if __name__ == "__main__":
    main()
