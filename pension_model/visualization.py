import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .calibration import gbpg, glg
from .simulation import NY

PALETTE = ["#1976D2", "#F57C00", "#388E3C", "#D32F2F", "#7B1FA2"]


def gen_figures(data, reg, results, stress, p, output_dir):
    _fig_contribution_gap(data, output_dir)
    _fig_historical_cashflow(data, output_dir)
    _fig_liability_regression(data, reg, output_dir)
    _fig_fan_charts(results, output_dir)
    _fig_projected_cashflow(results, output_dir)
    _fig_scenario_comparison(results, output_dir)
    _fig_historical_projection(data, results, output_dir)
    _fig_stress_tests(stress, output_dir)
    _fig_counterfactual(data, output_dir)
    _fig_tornado(output_dir)
    _fig_milestones(p, output_dir)


# ---------------------------------------------------------------------------
# Individual figure helpers
# ---------------------------------------------------------------------------

def _fig_contribution_gap(data, od):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(data["years"], 0, data["req_contrib"] / 1e3, alpha=0.3, color="blue", label="Required Contribution")
    ax.fill_between(data["years"], 0, data["actual_paid"] / 1e3, alpha=0.5, color="green", label="Actually Paid")
    ax.set_xlabel("Fiscal Year"); ax.set_ylabel("$ Millions")
    ax.set_title("Required vs. Actual Employer Contributions (2001-2024)", fontweight="bold")
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2)
    for i in range(0, len(data["years"]), 3):
        ax.annotate(
            f'{data["pct_paid"][i]*100:.0f}%',
            (data["years"][i], data["actual_paid"][i] / 1e3 + 20),
            ha="center", fontsize=7, color="darkgreen",
        )
    plt.tight_layout(); plt.savefig(f"{od}/fig_contribution_gap.png", dpi=200); plt.close()
    print("  fig_contribution_gap.png")


def _fig_historical_cashflow(data, od):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(data["years"],        data["actual_paid"] / 1e3,  width=0.35, label="Employer Paid",                    color="#388E3C", alpha=0.8)
    ax.bar(data["years"] + 0.35, data["ee_contrib"] / 1e3,   width=0.35, label="Employee Contributions (est.)",    color="#66BB6A", alpha=0.7)
    ax.plot(data["years"], data["benefit_payments"] / 1e3, "r-o", lw=2, markersize=4, label="Benefit Payments", zorder=5)
    ax.plot(data["years"], data["req_contrib"] / 1e3, "k--", lw=1.5, label="Required Employer Contribution", alpha=0.7)
    ax.set_xlabel("Fiscal Year"); ax.set_ylabel("$ Millions")
    ax.set_title("Historical Cash Flows: Contributions vs. Benefit Payments (2001-2024)", fontweight="bold")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.2, axis="y")
    plt.tight_layout(); plt.savefig(f"{od}/fig_historical_cashflow.png", dpi=180); plt.close()
    print("  fig_historical_cashflow.png")


def _fig_liability_regression(data, reg, od):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(data["years"], data["liabilities"] / 1e6, color="black", s=35, zorder=5, label="Actual", edgecolors="gray", linewidth=0.5)
    ax.plot(data["years"], reg["pq"] / 1e6, "--", color="#2196F3", lw=1.5, label=f'Quadratic ($R^2$={reg["r2q"]:.4f})')
    ax.plot(data["years"], reg["pc"] / 1e6, "--", color="#4CAF50", lw=1.5, label=f'Cubic ($R^2$={reg["r2c"]:.4f})')
    ax.plot(data["years"], reg["pe"] / 1e6, "-",  color="#E53935", lw=2.5, label=f'Exponential ($R^2$={reg["r2e"]:.4f})')
    ax.set_xlabel("Fiscal Year"); ax.set_ylabel("Actuarial Liabilities ($ Billions)")
    ax.set_title("Liability Regression Model Comparison (2001-2024)", fontweight="bold")
    ax.legend(fontsize=9, loc="upper left"); ax.grid(True, alpha=0.25)
    plt.tight_layout(); plt.savefig(f"{od}/fig_liability_regression.png", dpi=200); plt.close()
    print("  fig_liability_regression.png")


def _fig_fan_charts(results, od):
    ay = np.arange(2024, 2024 + NY + 1)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()
    for idx, (nm, res) in enumerate(results.items()):
        if idx >= 5:
            break
        ax = axes[idx]
        fp = res["funded_ratio"]
        p5  = np.percentile(fp,  5, axis=0) * 100
        p25 = np.percentile(fp, 25, axis=0) * 100
        p50 = np.percentile(fp, 50, axis=0) * 100
        p75 = np.percentile(fp, 75, axis=0) * 100
        p95 = np.percentile(fp, 95, axis=0) * 100
        ax.fill_between(ay, p5, p95, alpha=0.12, color=PALETTE[idx])
        ax.fill_between(ay, p25, p75, alpha=0.25, color=PALETTE[idx])
        ax.plot(ay, p50, color=PALETTE[idx], lw=2)
        ax.axhline(y=80, color="green",  ls="--", alpha=0.6, lw=0.8)
        ax.axhline(y=50, color="orange", ls="--", alpha=0.5, lw=0.8)
        ax.set_title(nm, fontsize=11, fontweight="bold")
        ax.set_xlabel("Year", fontsize=8); ax.set_ylabel("Funded Ratio (%)", fontsize=8)
        ax.set_ylim(0, 200); ax.grid(True, alpha=0.2); ax.tick_params(labelsize=7)
    axes[5].set_visible(False)
    plt.suptitle("Monte Carlo Funded Ratio Projections (10,000 Simulations)", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f"{od}/fig_fan_charts.png", dpi=180); plt.close()
    print("  fig_fan_charts.png")


def _fig_projected_cashflow(results, od):
    cy = np.arange(2025, 2025 + NY)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    mr = results["Moderate"]
    mc = np.median(mr["contributions"], axis=0)
    mb = np.median(mr["benefits"],      axis=0)
    ax.fill_between(cy,  0,   mc / 1e3, alpha=0.3, color="green", label="Total Contributions (median)")
    ax.fill_between(cy,  0,  -mb / 1e3, alpha=0.3, color="red",   label="Benefit Payments (median)")
    ax.plot(cy,  mc / 1e3, "g-", lw=2)
    ax.plot(cy, -mb / 1e3, "r-", lw=2)
    ax.plot(cy, (mc - mb) / 1e3, "k-", lw=2.5, label="Net Cash Flow")
    ax.axhline(y=0, color="black", lw=0.5)
    ax.set_xlabel("Year"); ax.set_ylabel("$ Millions")
    ax.set_title("Projected Cash Flows: Moderate Scenario (Median Path)", fontweight="bold")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.2)
    plt.tight_layout(); plt.savefig(f"{od}/fig_projected_cashflow.png", dpi=180); plt.close()
    print("  fig_projected_cashflow.png")


def _fig_scenario_comparison(results, od):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    ns   = ["Status\nQuo", "Conserv.", "Moderate", "Growth", "Aggress."]
    meds = [results[n]["median_fr"] * 100 for n in results]
    p80s = [results[n]["p80"]       * 100 for n in results]
    pins = [results[n]["p_insolv"]  * 100 for n in results]
    p5s  = [results[n]["p5"]        * 100 for n in results]
    p95s = [results[n]["p95"]       * 100 for n in results]

    axes[0].bar(ns, meds, color=PALETTE, alpha=0.85, edgecolor="gray", lw=0.5)
    axes[0].errorbar(ns, meds,
                     yerr=[[m - p for m, p in zip(meds, p5s)], [p - m for m, p in zip(meds, p95s)]],
                     fmt="none", color="black", capsize=3, lw=0.8)
    axes[0].axhline(y=80, color="green", ls="--", alpha=0.6)
    axes[0].set_title("Median Funded Ratio (2055)\n5th-95th Range", fontweight="bold", fontsize=10)
    axes[0].set_ylabel("Funded Ratio (%)")

    axes[1].bar(ns, p80s, color=PALETTE, alpha=0.85, edgecolor="gray", lw=0.5)
    axes[1].set_title("P(Funded >= 80%) by 2055", fontweight="bold", fontsize=10)
    axes[1].set_ylabel("Probability (%)")

    axes[2].bar(ns, pins, color=PALETTE, alpha=0.85, edgecolor="gray", lw=0.5)
    axes[2].set_title("P(Insolvency at Any Point)", fontweight="bold", fontsize=10)
    axes[2].set_ylabel("Probability (%)")

    plt.suptitle("Investment Strategy Comparison", fontsize=12, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(f"{od}/fig_scenario_comparison.png", dpi=180); plt.close()
    print("  fig_scenario_comparison.png")


def _fig_historical_projection(data, results, od):
    ay = np.arange(2024, 2024 + NY + 1)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(data["years"], data["funded_ratio"] * 100, "ko-", lw=2, ms=4, label="Historical", zorder=5)
    for idx, (nm, res) in enumerate(results.items()):
        p50 = np.percentile(res["funded_ratio"], 50, axis=0)
        ax.plot(ay, p50 * 100, color=PALETTE[idx], lw=1.8, alpha=0.85, label=nm)
    ax.axhline(y=80, color="green",     ls="--", alpha=0.5, label="80% Target")
    ax.axhline(y=90, color="darkgreen", ls=":",  alpha=0.4, label="90% Legislative Target")
    ax.axvspan(2025, 2054, alpha=0.04, color="blue")
    ax.set_xlabel("Year"); ax.set_ylabel("Funded Ratio (%)")
    ax.set_title("Historical & Projected Funded Ratio (2001-2055)", fontweight="bold")
    ax.legend(fontsize=7, loc="upper left", ncol=2); ax.grid(True, alpha=0.25); ax.set_xlim(2000, 2056)
    plt.tight_layout(); plt.savefig(f"{od}/fig_historical_projection.png", dpi=180); plt.close()
    print("  fig_historical_projection.png")


def _fig_stress_tests(stress, od):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    sn = list(stress.keys())
    sm = [stress[n]["median_fr"] * 100 for n in sn]
    sp = [stress[n]["p80"]       * 100 for n in sn]
    si = [stress[n]["p_insolv"]  * 100 for n in sn]
    x = np.arange(len(sn)); w = 0.35

    axes[0].bar(x - w / 2, sm, w, label="Median FR",   color="#1976D2", alpha=0.8)
    axes[0].bar(x + w / 2, sp, w, label="P(>=80%)",    color="#388E3C", alpha=0.8)
    axes[0].axhline(y=80, color="red", ls="--", alpha=0.5)
    axes[0].set_xticks(x); axes[0].set_xticklabels(sn, rotation=25, ha="right", fontsize=7)
    axes[0].set_ylabel("Percentage"); axes[0].set_title("Median FR & Success Probability", fontweight="bold")
    axes[0].legend(fontsize=8)

    axes[1].bar(x, si, color="#D32F2F", alpha=0.8)
    axes[1].set_xticks(x); axes[1].set_xticklabels(sn, rotation=25, ha="right", fontsize=7)
    axes[1].set_ylabel("Probability (%)"); axes[1].set_title("Insolvency Risk", fontweight="bold")

    plt.suptitle("Stress Test Results (Moderate Scenario)", fontsize=12, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(f"{od}/fig_stress_tests.png", dpi=180); plt.close()
    print("  fig_stress_tests.png")


def _fig_counterfactual(data, od):
    cfr = []; ce = 0
    for i in range(len(data["years"])):
        ret = data["inv_returns"][i]
        req = data["req_contrib"][i]
        act = data["actual_paid"][i]
        ce = ce * (1 + ret) + (req - act)
        cfr.append(min((data["assets"][i] + ce) / data["liabilities"][i] * 100, 120))
    afr = data["funded_ratio"] * 100

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(data["years"], afr, "r-o", lw=2.5, ms=5, label="Actual Funded Ratio",          zorder=5)
    ax.plot(data["years"], cfr, "g-s", lw=2.5, ms=5, label="If City Had Paid 100% Required", zorder=4)
    ax.fill_between(data["years"], afr, cfr, alpha=0.15, color="green")
    ax.axhline(y=80, color="black", ls="--", alpha=0.4, lw=1)
    ax.axhline(y=90, color="black", ls=":",  alpha=0.3, lw=1)
    ax.annotate("80% Target", xy=(2002, 82), fontsize=8, alpha=0.6)
    ax.annotate("90% Target", xy=(2002, 92), fontsize=8, alpha=0.6)
    ax.annotate(
        f"Gap: {cfr[-1]-afr[-1]:.0f}pp",
        xy=(2024, (afr[-1] + cfr[-1]) / 2),
        xytext=(2020, 60), fontsize=10, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="darkgreen"), color="darkgreen",
    )
    ax.set_xlabel("Fiscal Year", fontsize=11); ax.set_ylabel("Funded Ratio (%)", fontsize=11)
    ax.set_title("The Cost of Underfunding: Actual vs. Full-Compliance Counterfactual", fontweight="bold")
    ax.legend(fontsize=10, loc="lower left"); ax.grid(True, alpha=0.2); ax.set_ylim(15, 125)
    plt.tight_layout(); plt.savefig(f"{od}/fig_counterfactual.png", dpi=200); plt.close()
    print("  fig_counterfactual.png")


def _fig_tornado(od):
    fig, ax = plt.subplots(figsize=(10, 5))
    risks = [
        "Compliance\n(70% -> 100%)",
        "Contrib Growth\n(1.5% -> 3.5%)",
        "Market Returns\n(Stagflation -> Base)",
        "Liability Growth\n(Base -> +1pp)",
        "Payroll Growth\n(impact via EE)",
    ]
    lo   = [29, 43, 43, 51, 60]
    hi   = [108, 101, 68, 68, 75]
    base = 68

    for i, (r, l, h) in enumerate(zip(risks, lo, hi)):
        ax.barh(i, h - base, left=base, color="#388E3C", alpha=0.7, height=0.5, edgecolor="gray")
        ax.barh(i, l - base, left=base, color="#D32F2F", alpha=0.7, height=0.5, edgecolor="gray")
        ax.text(h + 1, i, f"{h}%", va="center", fontsize=9, fontweight="bold", color="#388E3C")
        ax.text(l - 1, i, f"{l}%", va="center", ha="right", fontsize=9, fontweight="bold", color="#D32F2F")

    ax.axvline(x=base, color="black", lw=1.5)
    ax.set_yticks(range(len(risks))); ax.set_yticklabels(risks, fontsize=9)
    ax.set_xlabel("Median Funded Ratio at 2055 (%)", fontsize=11)
    ax.set_title("Sensitivity Tornado: Which Variables Matter Most?", fontweight="bold")
    ax.set_xlim(10, 120); ax.axvline(x=80, color="green", ls="--", alpha=0.4)
    ax.annotate("80% Target", xy=(81, 4.3), fontsize=8, color="green", alpha=0.7)
    ax.grid(True, alpha=0.15, axis="x")
    plt.tight_layout(); plt.savefig(f"{od}/fig_tornado.png", dpi=200); plt.close()
    print("  fig_tornado.png")


def _fig_milestones(p, od):
    dy = list(range(2024, 2056))

    a = p["A0"]; req = p["REQ0"]; pay = p["PAY0"]; bp = p["BP0"]
    dfr = [p["A0"] / p["L0"] * 100]
    for yr in range(2025, 2056):
        req *= 1.025; er = 0.85 * req
        pay *= 1.035; ee = 0.085 * pay
        bp *= (1 + gbpg(yr))
        a = a * 1.065 + er + ee - bp - a * 0.005
        l = p["L0"] * np.prod([1 + glg(y) for y in range(2025, yr + 1)])
        dfr.append(a / l * 100)

    a2 = p["A0"]; r2 = p["REQ0"]; p2 = p["PAY0"]; b2 = p["BP0"]
    ffr = [p["A0"] / p["L0"] * 100]
    for yr in range(2025, 2056):
        r2 *= 1.025; er2 = 1.0 * r2
        p2 *= 1.035; ee2 = 0.085 * p2
        b2 *= (1 + gbpg(yr))
        a2 = a2 * 1.065 + er2 + ee2 - b2 - a2 * 0.005
        l2 = p["L0"] * np.prod([1 + glg(y) for y in range(2025, yr + 1)])
        ffr.append(a2 / l2 * 100)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dy, dfr, "b-", lw=2.5, label="85% Compliance (Base Case)")
    ax.plot(dy, ffr, "g-", lw=2.5, label="100% Compliance")

    for thr, clr, lbl in [
        (50, "orange",    "50% Milestone"),
        (65, "goldenrod", "65% Milestone"),
        (80, "green",     "80% Target"),
        (90, "darkgreen", "90% Legislative"),
    ]:
        ax.axhline(y=thr, color=clr, ls="--", alpha=0.5, lw=1)
        ax.annotate(lbl, xy=(2026, thr + 1), fontsize=8, color=clr)

    for thr, clr in [(50, "orange"), (65, "goldenrod"), (80, "green")]:
        for i, f in enumerate(dfr):
            if f >= thr:
                ax.plot(dy[i], f, "o", color=clr, ms=8, zorder=5)
                ax.annotate(f"{dy[i]}", xy=(dy[i], f + 2), fontsize=8, ha="center", color=clr, fontweight="bold")
                break

    ax.set_xlabel("Year", fontsize=11); ax.set_ylabel("Funded Ratio (%)", fontsize=11)
    ax.set_title("Projected Recovery Milestones (Deterministic, Growth Strategy)", fontweight="bold")
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2); ax.set_xlim(2024, 2056)
    plt.tight_layout(); plt.savefig(f"{od}/fig_milestones.png", dpi=200); plt.close()
    print("  fig_milestones.png")
