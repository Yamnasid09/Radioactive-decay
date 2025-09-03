import numpy as np
from dataclasses import dataclass
from .decay import Isotope

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
    - "binomial": fast, uses RNG binomial draws (recommended default)
    - "per_nucleus": simple/reference implementation (slow)
    - "numba": JIT-compiled per-nucleus engine (bonus; faster than plain per_nucleus)
    """
    t = np.arange(0, cfg.T + cfg.dt, cfg.dt)

    if cfg.engine == "numba":
        if not NUMBA_AVAILABLE:
            raise RuntimeError("Numba not available. Install numba or use engine='binomial'.")
        steps = t.size
        traj = np.empty((cfg.n_realizations, steps), dtype=np.float64)
        for r in range(cfg.n_realizations):
            traj[r, :] = _simulate_single_numba(iso.N0, iso.lam, cfg.dt, steps)
        return t, traj

    # Vectorized "binomial" engine: simulate all realizations in parallel per time-step
    if cfg.engine == "binomial":
        p = 1 - np.exp(-iso.lam * cfg.dt)
        steps = t.size
        R = cfg.n_realizations
        traj = np.empty((R, steps), dtype=np.float64)
        N = np.full(R, iso.N0, dtype=np.int64)
        traj[:, 0] = N
        for k in range(1, steps):
            decayed = rng.binomial(N, p)  # vectorized across realizations
            N = N - decayed
            traj[:, k] = N
        return t, traj

    # Reference "per_nucleus" engine (slow; for correctness/teaching)
    p = 1 - np.exp(-iso.lam * cfg.dt)
    traj = np.zeros((cfg.n_realizations, t.size), dtype=float)
    for r in range(cfg.n_realizations):
        N = iso.N0
        traj[r, 0] = N
        for k in range(1, t.size):
            decayed = (rng.random(N) < p).sum()
            N -= decayed
            traj[r, k] = N
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
