import numpy as np
from scipy import stats
# Helper functions for averages, confidence intervals, and lambda fit

def mean_and_ci(traj, alpha=0.05):
    """
    Compute mean and confidence interval across realizations.

    Parameters
    ----------
    traj : np.ndarray
        Matrix of realizations (n_realizations x n_time).
    alpha : float
        Significance level for confidence interval (default=0.05 for 95% CI).

    Returns
    -------
    mean : np.ndarray
        Mean across realizations
    half : np.ndarray
        Half-width of confidence interval
    """
    m = traj.mean(axis=0)
    s = traj.std(axis=0, ddof=1)
    n = traj.shape[0]
    tcrit = stats.t.ppf(1 - alpha/2, df=n-1)
    half = tcrit * s / np.sqrt(n)
    return m, half


def fit_lambda_from_counts(t, counts):
    """
    Fit lambda by linear regression on log(N(t)).

    Parameters
    ----------
    t : np.ndarray
        Time array
    counts : np.ndarray
        Mean counts at each time

    Returns
    -------
    lam_hat : float
        Estimated decay constant
    N0_hat : float
        Estimated initial count
    r2 : float
        R^2 of the fit
    """
    mask = counts > 0
    slope, intercept, r, *_ = stats.linregress(t[mask], np.log(counts[mask]))
    lam_hat = -slope
    N0_hat = np.exp(intercept)
    return lam_hat, N0_hat, r**2
