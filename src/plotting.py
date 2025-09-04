# plotting.py
# All functions use 4-space indentation (no tabs).

# Minimal plotting helpers for counts, log-counts, activity, and measured counts

import numpy as np
import matplotlib.pyplot as plt


def _save_show(path, show):
    if path:
        plt.savefig(path, bbox_inches="tight", dpi=200)
    if show:
        plt.show()
    plt.close()


def plot_counts(t, mean, ci=None, label=None, path=None, show=False):
    """
    Plot N(t) with an optional symmetric confidence band 'ci'.
    """
    plt.figure()
    plt.plot(t, mean, label=label)
    if ci is not None:
        lo = np.maximum(mean - ci, 0.0)
        hi = mean + ci
        plt.fill_between(t, lo, hi, alpha=0.2)
    plt.xlabel("time [s]")
    plt.ylabel("N(t)")
    if label:
        plt.legend()
    _save_show(path, show)


def plot_log_counts(t, mean, label=None, path=None, show=False):
    """
    Plot log N(t) vs time (only where N>0).
    """
    valid = mean > 0
    plt.figure()
    plt.plot(t[valid], np.log(mean[valid]), label=label)
    plt.xlabel("time [s]")
    plt.ylabel("log N(t)")
    if label:
        plt.legend()
    _save_show(path, show)


def plot_activity(t, A, label=None, path=None, show=False):
    """
    Plot activity A(t) vs time.
    """
    plt.figure()
    plt.plot(t, A, label=label)
    plt.xlabel("time [s]")
    plt.ylabel("Activity A(t)")
    if label:
        plt.legend()
    _save_show(path, show)


def plot_measured_counts(t, counts, label=None, path=None, show=False):
    """
    Plot measured detector counts per time bin (e.g., Poisson-thinned decays).
    """
    plt.figure()
    plt.step(t, counts, where="mid", label=label)
    plt.xlabel("time [s]")
    plt.ylabel("Measured counts per bin")
    if label:
        plt.legend()
    _save_show(path, show)


