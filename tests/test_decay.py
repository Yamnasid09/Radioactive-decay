import numpy as np
from src.decay import Isotope
from src.simulate import SimConfig, simulate_isotope


def test_half_life_relationship():
    """
    Verify that the half-life property matches what was given.
    """
    iso = Isotope("X", N0=1000, half_life=10.0)
    assert np.isclose(iso.half_life, 10.0)


def test_exponential_behavior_matches_fit():
    """
    Run a Monte Carlo simulation and check that at one half-life,
    the population is ~half the original.
    """
    iso = Isotope("X", N0=50000, half_life=5.0)
    cfg = SimConfig(dt=0.05, T=5.0*5, n_realizations=30, engine="binomial")
    t, traj = simulate_isotope(iso, cfg, np.random.default_rng(0))

    idx = np.argmin(np.abs(t - iso.half_life))
    meanN = traj.mean(axis=0)
    # At t = T1/2, N should be between 40–60% of N0
    assert 0.4 < meanN[idx]/iso.N0 < 0.6
