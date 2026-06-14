import csv
import os
import sys

import numpy as np


DEFAULT_CSV = "filtered_chicago_filtered_chicago_.csv"


def load_data(filepath=None):
    if filepath is None:
        filepath = DEFAULT_CSV
    if not os.path.exists(filepath):
        print("=" * 60)
        print("DATA FILE REQUIRED")
        print("=" * 60)
        print("Please provide the path to the Public Plans Database CSV")
        print(f"(Expected: {DEFAULT_CSV})")
        filepath = input("Enter file path: ").strip() or DEFAULT_CSV
    if not os.path.exists(filepath):
        print(f"\nERROR: File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        rows = [r for r in csv.DictReader(f) if r["PlanName"] == "Chicago (IL) Municipal"]
    if not rows:
        print("ERROR: No Chicago Municipal data found.")
        sys.exit(1)

    rows.sort(key=lambda r: int(r["fy"]))
    print(f"Loaded {len(rows)} years ({rows[0]['fy']}-{rows[-1]['fy']})")
    return rows


def extract(rows):
    d = {}
    d["years"] = np.array([int(r["fy"]) for r in rows])
    d["liabilities"] = np.array([float(r["ActLiabilities_GASB"]) for r in rows])
    d["assets"] = np.array([float(r["MktAssets_net"]) for r in rows])
    d["funded_ratio"] = np.array([float(r["ActFundedRatio_GASB"]) for r in rows])
    d["beneficiaries"] = np.array([float(r["beneficiaries_tot"]) for r in rows])
    d["ben_avg"] = np.array([float(r["BeneficiaryBenefit_avg"]) for r in rows])
    d["actives"] = np.array([float(r["actives_tot"]) for r in rows])
    d["salary_avg"] = np.array([float(r["ActiveSalary_avg"]) for r in rows])
    d["req_contrib"] = np.array([float(r["RequiredContribution"]) for r in rows])
    d["pct_paid"] = np.array([float(r["PercentReqContPaid"]) for r in rows])
    d["inv_returns"] = np.array([float(r["InvestmentReturn_1yr"]) for r in rows])
    d["benefit_payments"] = d["beneficiaries"] * d["ben_avg"]
    d["payroll"] = d["actives"] * d["salary_avg"]
    d["actual_paid"] = d["req_contrib"] * d["pct_paid"]
    d["ee_contrib"] = d["payroll"] * 0.085
    return d
