import matplotlib.pyplot as plt
import numpy as np

def plot_counts(t, mean_counts, ci=None, label=None, path=None, show=False):
    """
    Plot mean counts with optional confidence interval.
    """
    plt.figure()
    plt.plot(t, mean_counts, label=label)
    if ci is not None:
        plt.fill_between(t, mean_counts-ci, mean_counts+ci, alpha=0.3)
    plt.xlabel("time [s]")
    plt.ylabel("N(t)")
    if label:
        plt.legend()
    if path:
        plt.savefig(path, bbox_inches="tight", dpi=200)
    if show:
        plt.show()
    plt.close()


def plot_log_counts(t, counts, label=None, path=None, show=False):
    """
    Plot log of counts vs time.
    """
    plt.figure()
    plt.plot(t, np.log(np.maximum(counts, 1e-12)), label=label)
    plt.xlabel("time [s]")
    plt.ylabel("log N(t)")
    if label:
        plt.legend()
    if path:
        plt.savefig(path, bbox_inches="tight", dpi=200)
    if show:
        plt.show()
    plt.close()


def plot_activity(t, activity, label=None, path=None, show=False):
    """
    Plot activity vs time.
    """
    plt.figure()
    plt.plot(t, activity, label=label)
    plt.xlabel("time [s]")
    plt.ylabel("Activity A(t)")
    if label:
        plt.legend()
    if path:
        plt.savefig(path, bbox_inches="tight", dpi=200)
    if show:
        plt.show()
    plt.close()
