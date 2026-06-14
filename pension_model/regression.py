import numpy as np
from scipy.optimize import curve_fit


def fit_regression(data):
    t = data["years"] - data["years"][0]
    L = data["liabilities"]

    cq = np.polyfit(t, L, 2)
    pq = np.polyval(cq, t)
    r2q = 1 - np.sum((L - pq) ** 2) / np.sum((L - np.mean(L)) ** 2)

    cc = np.polyfit(t, L, 3)
    pc = np.polyval(cc, t)
    r2c = 1 - np.sum((L - pc) ** 2) / np.sum((L - np.mean(L)) ** 2)

    def ef(t, a, b, c):
        return a * np.exp(b * t) + c

    po, _ = curve_fit(ef, t, L, p0=[5e6, 0.05, 1e6], maxfev=10000)
    pe = ef(t, *po)
    r2e = 1 - np.sum((L - pe) ** 2) / np.sum((L - np.mean(L)) ** 2)

    return {"pq": pq, "r2q": r2q, "pc": pc, "r2c": r2c, "pe": pe, "r2e": r2e}
