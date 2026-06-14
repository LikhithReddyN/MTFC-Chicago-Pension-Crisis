import numpy as np

from .calibration import gbpg, glg

N = 10_000
NY = 30

SCENARIOS = {
    "Status Quo":  {"eq": .473, "fi": .197, "alt": .232, "cash": .098},
    "Conservative":{"eq": .30,  "fi": .50,  "alt": .10,  "cash": .10},
    "Moderate":    {"eq": .50,  "fi": .30,  "alt": .15,  "cash": .05},
    "Growth":      {"eq": .60,  "fi": .20,  "alt": .18,  "cash": .02},
    "Aggressive":  {"eq": .70,  "fi": .10,  "alt": .18,  "cash": .02},
}


def run_sim(sc, p, n=N, rg=None, pg=None, cc=None, oret=None, sy=0, la=0.0):
    """
    Run a Monte Carlo simulation for a given asset allocation scenario.

    Parameters
    ----------
    sc   : scenario dict with keys eq, fi, alt, cash
    p    : calibrated parameter dict from calibrate()
    n    : number of simulation paths
    rg   : required-contribution annual growth override
    pg   : payroll annual growth override
    cc   : employer compliance cap override
    oret : override investment return for the first `sy` years (stress test)
    sy   : number of years to apply the override return
    la   : additive liability growth shock (e.g. 0.01 = +1 pp)
    """
    if rg is None:
        rg = p["REQ_G"]
    if pg is None:
        pg = p["PAY_G"]
    if cc is None:
        cc = p["COMP_CAP"]

    w = np.array([sc["eq"], sc["fi"], sc["alt"]])
    wc = sc["cash"]
    m = p["means"]
    s = p["stds"]

    aa = np.zeros((n, NY + 1))
    ll = np.zeros((n, NY + 1))
    fr = np.zeros((n, NY + 1))
    ca = np.zeros((n, NY))
    ba = np.zeros((n, NY))

    aa[:, 0] = p["A0"]
    ll[:, 0] = p["L0"]
    fr[:, 0] = p["A0"] / p["L0"]

    for si in range(n):
        a, l, bp, req, pay = p["A0"], p["L0"], p["BP0"], p["REQ0"], p["PAY0"]
        for yi in range(NY):
            yr = 2025 + yi
            if oret is not None and yi < sy:
                pr = oret
            else:
                z = np.random.standard_normal(3)
                ch = p["L_crisis"] if fr[si, yi] < 0.20 else p["L_chol"]
                cz = ch @ z
                lr_ = np.exp((m - s ** 2 / 2) + s * cz) - 1
                pr = np.dot(w, lr_) + wc * p["CASH"]

            req *= (1 + rg)
            bc = min(p["COMP0"] + (cc - p["COMP0"]) * (yr - 2024) / 3, cc) if yr <= 2027 else cc
            if pr < -0.10:
                sh = np.random.uniform(-0.15, -0.05)
            elif pr < 0:
                sh = np.random.uniform(-0.08, 0)
            else:
                sh = np.random.uniform(-0.02, 0.03)

            comp = np.clip(bc + sh, 0.40, cc)
            er = comp * req
            pay *= (1 + pg)
            ee = p["EE"] * pay
            tot = er + ee
            bp *= (1 + gbpg(yr))
            adm = a * p["ADMIN"]
            a = a * (1 + pr) + tot - bp - adm
            if a < 0:
                a = 0
            l *= (1 + glg(yr) + la)

            aa[si, yi + 1] = a
            ll[si, yi + 1] = l
            fr[si, yi + 1] = a / l if l > 0 else 0
            ca[si, yi] = tot
            ba[si, yi] = bp

    ff = fr[:, -1]
    return {
        "assets": aa,
        "liabilities": ll,
        "funded_ratio": fr,
        "contributions": ca,
        "benefits": ba,
        "median_fr": np.median(ff),
        "p5":        np.percentile(ff, 5),
        "p25":       np.percentile(ff, 25),
        "p75":       np.percentile(ff, 75),
        "p95":       np.percentile(ff, 95),
        "p80":       np.mean(ff >= 0.8),
        "p90":       np.mean(ff >= 0.9),
        "p50":       np.mean(ff >= 0.5),
        "p_insolv":  np.mean(np.any(aa == 0, axis=1)),
    }
