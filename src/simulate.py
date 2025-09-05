import numpy as np
from dataclasses import dataclass
from .decay import Isotope
# Monte Carlo engines for radioactive decay (binomial default; optional Numba)

# --- Optional: Numba JIT for speed (fallback-safe) ---
try:
    from numba import njit
    NUMBA_AVAILABLE = True
except Exception:
    NUMBA_AVAILABLE = False
    def njit(*args, **kwargs):
        def _wrap(f): return f
        return _wrap


@dataclass
class SimConfig:
    dt: float
    T: float
    n_realizations: int
    engine: str = "binomial"   # "binomial" (fast), "per_nucleus" (slow), "numba" (JIT per-nucleus)


def simulate_isotope(iso: Isotope, cfg: SimConfig, rng: np.random.Generator):
    """
    Simulate radioactive decay of a single isotope.

    Engines
    -------
    - "binomial": fast, RNG binomial draws (recommended default)
    - "per_nucleus": simple/reference implementation (slow)
    - "numba": JIT per-nucleus engine (bonus; faster than plain per_nucleus)
    """
    t = np.arange(0, cfg.T + cfg.dt, cfg.dt)

    # ---- NUMBA branch ----
    if cfg.engine == "numba":
        if not NUMBA_AVAILABLE:
            raise RuntimeError("Numba not available. Install numba or use engine='binomial'.")
        steps = t.size
        traj = np.empty((cfg.n_realizations, steps), dtype=np.float64)
        for r in range(cfg.n_realizations):
            traj[r, :] = _simulate_single_numba(iso.N0, iso.lam, cfg.dt, steps)

        N_mean = traj.mean(axis=0).astype(float)
        _save_run(
            {"t": t, "N": N_mean, "traj": traj},
            {"mode": "numba", "n0": iso.N0, "lambda": iso.lam, "tmax": cfg.T, "dt": cfg.dt,
             "n_realizations": cfg.n_realizations}
        )
        return t, traj

    # ---- BINOMIAL branch (vectorized over realizations) ----
    if cfg.engine == "binomial":
        p = 1.0 - np.exp(-iso.lam * cfg.dt)
        steps = t.size
        R = cfg.n_realizations
        traj = np.empty((R, steps), dtype=np.float64)

        N = np.full(R, iso.N0, dtype=np.int64)
        traj[:, 0] = N
        for k in range(1, steps):
            decayed = rng.binomial(N, p)
            N = N - decayed
            traj[:, k] = N

        N_mean = traj.mean(axis=0).astype(float)
        _save_run(
            {"t": t, "N": N_mean, "traj": traj},
            {"mode": "binomial", "n0": iso.N0, "lambda": iso.lam, "tmax": cfg.T, "dt": cfg.dt,
             "n_realizations": cfg.n_realizations}
        )
        return t, traj

    # ---- PER-NUCLEUS reference branch (slow) ----
    p = 1.0 - np.exp(-iso.lam * cfg.dt)
    steps = t.size
    R = cfg.n_realizations
    traj = np.zeros((R, steps), dtype=float)
    for r in range(R):
        n = iso.N0
        traj[r, 0] = n
        for k in range(1, steps):
            decayed = (rng.random(n) < p).sum()
            n -= decayed
            traj[r, k] = n

    N_mean = traj.mean(axis=0).astype(float)
    _save_run(
        {"t": t, "N": N_mean, "traj": traj},
        {"mode": "per_nucleus", "n0": iso.N0, "lambda": iso.lam, "tmax": cfg.T, "dt": cfg.dt,
         "n_realizations": cfg.n_realizations}
    )
    return t, traj



@njit
def _simulate_single_numba(N0: int, lam: float, dt: float, steps: int):
    """
    JIT-compiled per-nucleus simulation for one realization.
    NOTE: Use with moderate N0 or realizations; default 'binomial' is fastest overall.
    """
    p = 1 - np.exp(-lam * dt)
    traj = np.empty(steps, dtype=np.float64)
    traj[0] = N0
    N = N0
    for k in range(1, steps):
        decayed = 0
        # per-nucleus thinning
        for i in range(N):
            if np.random.random() < p:
                decayed += 1
        N -= decayed
        traj[k] = N
    return traj

# --- saving helper (append at file bottom) ---
def _save_run(arrays: dict, meta: dict):
    from pathlib import Path
    import numpy as np, json, time

    out_root = Path("data/runs")
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = out_root / time.strftime("run_%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    for k, v in arrays.items():
        v = np.asarray(v)
        np.save(run_dir / f"{k}.npy", v)
        np.savetxt(run_dir / f"{k}.csv", v, delimiter=",")

    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    # update 'last' symlink
    last = out_root / "last"
    try:
        if last.exists() or last.is_symlink():
            last.unlink()
        last.symlink_to(run_dir.resolve())
    except Exception:
        pass  # e.g., Windows without symlink perms

    print(f"[OK] Saved results to: {run_dir}")
