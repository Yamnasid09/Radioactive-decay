import argparse, os, json
import numpy as np
import matplotlib.pyplot as plt

def load_series(run_dir: str):
    t = np.load(os.path.join(run_dir, "t.npy"))
    N = None
    for cand in ("N.npy","counts.npy"):
        p = os.path.join(run_dir, cand)
        if os.path.exists(p):
            N = np.load(p).astype(float); break
    if N is None:
        p = os.path.join(run_dir, "traj.npy")
        if os.path.exists(p):
            N = np.load(p).mean(axis=0).astype(float)
        else:
            raise SystemExit("No N.npy/counts.npy/traj.npy in run dir.")
    return t, N

def fit_lambda(t, N):
    msk = N > 0
    tt, yy = t[msk], np.log(N[msk])
    if tt.size < 2:
        raise SystemExit("Not enough positive counts to fit.")
    m, c = np.polyfit(tt, yy, 1)   # ln N ≈ m t + c
    lam_hat = -m
    half = np.log(2) / lam_hat if lam_hat > 0 else np.nan
    return lam_hat, half, (m, c), msk

def main():
    ap = argparse.ArgumentParser(description="Estimate decay constant and half-life from a saved run")
    ap.add_argument("--run-dir", default="data/runs/last")
    ap.add_argument("--out", default="images")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    t, N = load_series(args.run_dir)
    lam_hat, half, (m,c), msk = fit_lambda(t, N)

    # Save JSON report
    rep = {"lambda_hat": float(lam_hat), "half_life_hat": float(half), "points_used": int(msk.sum())}
    with open(os.path.join(args.run_dir, "fit.json"), "w") as f:
        json.dump(rep, f, indent=2)

    # Plot log fit
    import numpy as np  # ensure np in this scope
    x = np.array([t[msk].min(), t[msk].max()])
    y = m*x + c
    plt.figure()
    plt.plot(t[msk], np.log(N[msk]), ".", label="log counts")
    plt.plot(x, y, label=f"fit slope = {-lam_hat:.4f} (=> λ̂={lam_hat:.4f})")
    plt.xlabel("Time (simulation units)")
    plt.ylabel("ln N")
    plt.title(f"Half-life ≈ {half:.4f} (same units as time)")
    plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
    outp = os.path.join(args.out, "log_fit.png")
    plt.savefig(outp, dpi=200)

    print(f"[OK] λ̂={lam_hat:.6f}, T1/2≈{half:.6f}. Saved plot to {outp} and JSON to {args.run_dir}/fit.json")

if __name__ == "__main__":
    main()
