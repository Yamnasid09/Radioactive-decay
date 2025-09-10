import numpy as np
from src.chain import ChainParams, simulate_chain_deterministic, simulate_chain_mc

def _analytic_chain(N0A, lamA, lamB, t):
    NA = N0A * np.exp(-lamA * t)
    if abs(lamA - lamB) < 1e-12:
        NB = lamA * N0A * t * np.exp(-lamA * t)
    else:
        NB = (lamA * N0A) / (lamB - lamA) * (np.exp(-lamA * t) - np.exp(-lamB * t))
    return NA, NB

def test_deterministic_matches_analytic():
    N0A, lamA, lamB = 10000, 0.2, 0.05
    dt, T = 0.01, 10.0
    t, NA, NB = simulate_chain_deterministic(ChainParams(N0A, lamA, lamB), dt, T)
    NA2, NB2 = _analytic_chain(N0A, lamA, lamB, t)
    assert np.allclose(NA, NA2, rtol=1e-12, atol=0.0)
    assert np.allclose(NB, NB2, rtol=1e-12, atol=0.0)
    # sanity: NA must be non-increasing
    assert np.all(np.diff(NA) <= 1e-12)

def test_mc_converges_to_deterministic_mean():
    # modest sizes to keep CI fast
    N0A, lamA, lamB = 5000, 0.2, 0.05
    dt, T, R, seed = 0.05, 10.0, 120, 42
    t, NA_det, NB_det = simulate_chain_deterministic(ChainParams(N0A, lamA, lamB), dt, T)
    rng = np.random.default_rng(seed)
    t2, NA_traj, NB_traj = simulate_chain_mc(ChainParams(N0A, lamA, lamB), dt, T, R, rng)
    assert np.allclose(t, t2)
    NA_mean, NB_mean = NA_traj.mean(axis=0), NB_traj.mean(axis=0)

    def rmse_rel(a, b):
        denom = np.maximum(np.abs(b), 1.0)
        return float(np.sqrt(np.mean(((a - b) / denom) ** 2)))

    # MC mean should be close to deterministic (law of large numbers)
    assert rmse_rel(NA_mean, NA_det) < 0.05
    assert rmse_rel(NB_mean, NB_det) < 0.08  # NB is noisier; allow a bit more
