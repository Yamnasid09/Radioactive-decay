import numpy as np
from dataclasses import dataclass
from .decay import Isotope

@dataclass
class SimConfig:
    dt: float
    T: float
    n_realizations: int
    engine: str = "binomial"


def simulate_isotope(iso: Isotope, cfg: SimConfig, rng: np.random.Generator):
    """
    Simulate radioactive decay of a single isotope using Monte Carlo.
    
    Parameters
    ----------
    iso : Isotope
        The isotope to simulate.
    cfg : SimConfig
        Simulation configuration (dt, total time, realizations, engine).
    rng : np.random.Generator
        Random number generator.
    
    Returns
    -------
    t : np.ndarray
        Time array
    traj : np.ndarray
        Matrix of realizations (shape: n_realizations x n_time)
    """
    t = np.arange(0, cfg.T + cfg.dt, cfg.dt)
    p = 1 - np.exp(-iso.lam * cfg.dt)
    traj = np.zeros((cfg.n_realizations, t.size), dtype=float)

    for r in range(cfg.n_realizations):
        N = iso.N0
        traj[r, 0] = N
        for k in range(1, t.size):
            if cfg.engine == "binomial":
                decayed = rng.binomial(N, p)
            else:  # per nucleus (slower)
                decayed = (rng.random(N) < p).sum()
            N -= decayed
            traj[r, k] = N
    return t, traj
