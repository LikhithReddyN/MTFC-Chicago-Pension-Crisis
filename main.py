"""
Chicago Municipal Employees' Pension Fund — Monte Carlo Simulation Model
MTFC 2025-26 Competition | Team #23834

Usage:
    python main.py
    python main.py path/to/data.csv
"""

import os
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
np.random.seed(42)

from pension_model.annuity import annuity
from pension_model.calibration import calibrate, glg
from pension_model.data_loader import extract, load_data
from pension_model.regression import fit_regression
from pension_model.simulation import N, NY, SCENARIOS, run_sim
from pension_model.visualization import gen_figures


def main():
    print("=" * 70)
    print("CHICAGO MUNICIPAL PENSION FUND - MONTE CARLO MODEL")
    print("=" * 70)

    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = "output_figures"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Figures will be saved to: {output_dir}/\n")

    rows = load_data(filepath)
    data = extract(rows)
    p    = calibrate(rows, data)

    print("\n--- Parameters ---")
    print(f"Assets: ${p['A0']/1e6:.2f}B | Liabilities: ${p['L0']/1e6:.2f}B | FR: {p['A0']/p['L0']*100:.1f}%")
    print(f"Total fund return: arith={p['total_arith']*100:.2f}%, geom={p['total_geom']*100:.2f}%, sd={p['total_std']*100:.2f}%")
    print(f"Liability growth: {p['LIAB_BASE']*100:.2f}% | BP growth: {p['BP_BASE']*100:.2f}%")
    print(f"Req contrib growth (hist): {p['REQ_HIST']*100:.2f}% -> model: {p['REQ_G']*100:.1f}%")

    reg = fit_regression(data)
    print("\n--- Regression ---")
    print(f"Quad R2={reg['r2q']:.4f}  Cubic R2={reg['r2c']:.4f}  Exp R2={reg['r2e']:.4f}")

    print(f"\n--- Main Scenarios ({N} sims) ---")
    results = {}
    for nm, sc in SCENARIOS.items():
        r = run_sim(sc, p)
        results[nm] = r
        print(f"  {nm:<16} Med={r['median_fr']*100:>5.1f}%  [{r['p5']*100:.0f}%-{r['p95']*100:.0f}%]  "
              f"P80={r['p80']*100:.1f}%  P50={r['p50']*100:.1f}%  Ins={r['p_insolv']*100:.1f}%")

    print("\n--- Stress Tests (Moderate, 5000 sims) ---")
    mod = SCENARIOS["Moderate"]
    stress = {}
    tests = [
        ("Low Contrib Growth (1.5%)",    dict(rg=0.015)),
        ("High Contrib Growth (3.5%)",   dict(rg=0.035)),
        ("Compliance Cap 70%",           dict(cc=0.70)),
        ("Full Compliance (100%)",       dict(cc=1.00)),
        ("Liability Growth +1pp",        dict(la=0.01)),
        ("Stagflation (5yr)",            dict(oret=0.0, sy=5, pg=0.02)),
        ("Combined Crisis",              dict(oret=-0.15, sy=3, pg=0.02, rg=0.01, cc=0.70)),
    ]
    for lb, kw in tests:
        r = run_sim(mod, p, n=5000, **kw)
        stress[lb] = r
        print(f"  {lb:<30} Med={r['median_fr']*100:>5.1f}%  P80={r['p80']*100:.1f}%  Ins={r['p_insolv']*100:.1f}%")

    ann = annuity(data)
    print("\n--- Annuity ---")
    print(f"  Full: ${ann['full']/1e6:.2f}B  Partial: ${ann['partial']/1e6:.2f}B")

    print("\n--- Generating Figures ---")
    gen_figures(data, reg, results, stress, p, output_dir)

    pl = p["L0"] * np.prod([1 + glg(y) for y in range(2025, 2056)])
    print("\n--- Projections ---")
    print(f"  Liabilities 2055: ${pl/1e6:.1f}B  Req contrib 2055: ${p['REQ0']*1.025**31/1e3:.1f}M")
    print(f"\n{'='*70}\nCOMPLETE. Figures in {output_dir}/\n{'='*70}")


if __name__ == "__main__":
    main()
