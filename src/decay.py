import numpy as np

class Isotope:
    def __init__(self, name: str, N0: int, half_life: float = None, lam: float = None):
        # Either half_life OR lambda must be given, not both
        if (half_life is None) == (lam is None):
            raise ValueError("Provide exactly one of half_life or lam")
        self.name = name
        self.N0 = int(N0)
        self.lam = np.log(2)/half_life if lam is None else float(lam)

    @property
    def half_life(self):
        return np.log(2)/self.lam

    def N_analytical(self, t):
        return self.N0 * np.exp(-self.lam * t)

    def activity(self, t):
        return self.lam * self.N_analytical(t)


def mixture_counts_analytical(isotopes, t):
    N = sum(iso.N_analytical(t) for iso in isotopes)
    A = sum(iso.activity(t) for iso in isotopes)
    return N, A
