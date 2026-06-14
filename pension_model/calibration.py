import numpy as np


def glg(yr, base=0.0358):
    """Liability growth rate — tapers from historical base to 2.5% by 2050."""
    if yr <= 2030:
        return base
    elif yr >= 2050:
        return 0.025
    return base + (0.025 - base) * (yr - 2030) / 20


def gbpg(yr, base=0.0354):
    """Benefit payment growth rate — tapers from historical base to 2.5% by 2050."""
    if yr <= 2035:
        return base
    elif yr >= 2050:
        return 0.025
    return base + (0.025 - base) * (yr - 2035) / 15


def calibrate(rows, data):
    p = {}

    eq = [float(r["EQTotal_Rtrn"]) for r in rows if r["EQTotal_Rtrn"] and float(r["EQTotal_Rtrn"]) != 0]
    fi = [float(r["FITotal_Rtrn"]) for r in rows if r["FITotal_Rtrn"] and float(r["FITotal_Rtrn"]) != 0]
    p["means"] = np.array([np.mean(eq), np.mean(fi), 0.07])
    p["stds"] = np.array([np.std(eq, ddof=1), np.std(fi, ddof=1), 0.15])

    p["total_arith"] = np.mean(data["inv_returns"])
    p["total_geom"] = np.prod([1 + r for r in data["inv_returns"]]) ** (1 / len(data["inv_returns"])) - 1
    p["total_std"] = np.std(data["inv_returns"], ddof=1)

    p["A0"] = data["assets"][-1]
    p["L0"] = data["liabilities"][-1]
    p["BP0"] = data["benefit_payments"][-1]
    p["REQ0"] = data["req_contrib"][-1]
    p["PAY0"] = data["payroll"][-1]
    p["COMP0"] = data["pct_paid"][-1]

    m = data["years"] >= 2016
    lr = data["liabilities"][m]
    p["LIAB_BASE"] = np.mean(np.diff(lr) / lr[:-1])

    bg = np.diff(data["benefit_payments"]) / data["benefit_payments"][:-1]
    p["BP_BASE"] = np.mean(bg[data["years"][1:] >= 2016])

    rg = []
    for i in range(1, len(data["req_contrib"])):
        if data["years"][i] >= 2017:
            rg.append((data["req_contrib"][i] - data["req_contrib"][i - 1]) / data["req_contrib"][i - 1])
    p["REQ_HIST"] = np.mean(rg)

    p["REQ_G"] = 0.025
    p["PAY_G"] = 0.035
    p["COMP_CAP"] = 0.85
    p["EE"] = 0.085
    p["CASH"] = 0.04
    p["ADMIN"] = 0.005

    # Cholesky factors for correlated asset returns (normal and crisis regimes)
    p["L_chol"] = np.linalg.cholesky(np.array([[1, .1, .55], [.1, 1, .2], [.55, .2, 1]]))
    p["L_crisis"] = np.linalg.cholesky(np.array([[1, .4, .85], [.4, 1, .5], [.85, .5, 1]]))

    return p
