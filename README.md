# Chicago Municipal Pension Fund — Monte Carlo Simulation Model

> MTFC 2025-26 Competition | Team #23834

A stochastic actuarial model that projects the funded-ratio trajectory of the
**Chicago (IL) Municipal Employees' Pension Fund** through 2055 using Monte Carlo
simulation, multi-asset return modelling, and stress testing.

---

## Features

| Module | What it does |
|--------|-------------|
| `data_loader` | Reads Public Plans Database CSV, filters Chicago Municipal rows |
| `calibration` | Derives return distributions, liability/benefit growth rates, Cholesky correlation matrices |
| `regression` | Fits quadratic, cubic, and exponential liability trend models |
| `simulation` | Runs 10,000-path Monte Carlo across five investment strategies |
| `annuity` | Computes present-value of full and partial annuity obligations |
| `visualization` | Generates 11 publication-quality figures |

### Investment strategies modelled

| Strategy | Equity | Fixed Income | Alternatives | Cash |
|----------|--------|-------------|--------------|------|
| Status Quo | 47.3% | 19.7% | 23.2% | 9.8% |
| Conservative | 30% | 50% | 10% | 10% |
| Moderate | 50% | 30% | 15% | 5% |
| Growth | 60% | 20% | 18% | 2% |
| Aggressive | 70% | 10% | 18% | 2% |

### Stress tests

- Low / High contribution growth (1.5% vs 3.5%)
- Employer compliance cap (70% vs 100%)
- Liability growth shock (+1 pp)
- Stagflation (5-year zero return)
- Combined crisis (market crash + low compliance + low growth)

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/<your-org>/chicago-pension-crisis.git
cd chicago-pension-crisis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place your data file in the repo root
#    Expected filename: filtered_chicago_filtered_chicago_.csv
#    Source: Public Plans Database (publicplansdata.org)

# 4. Run
python main.py
# or provide a custom path:
python main.py path/to/your_data.csv
```

Figures are written to `output_figures/`.

---

## Repository structure

```
chicago-pension-crisis/
├── main.py                      # Entry point — orchestrates all steps
├── requirements.txt
├── .gitignore
└── pension_model/
    ├── __init__.py
    ├── data_loader.py           # load_data(), extract()
    ├── calibration.py           # calibrate(), glg(), gbpg()
    ├── regression.py            # fit_regression()
    ├── simulation.py            # run_sim(), SCENARIOS
    ├── annuity.py               # annuity()
    └── visualization.py        # gen_figures() and 11 sub-figures
```

---

## Output figures

| File | Description |
|------|-------------|
| `fig_contribution_gap.png` | Required vs. actual employer contributions 2001-2024 |
| `fig_historical_cashflow.png` | Contributions vs. benefit payments (bar chart) |
| `fig_liability_regression.png` | Quadratic / cubic / exponential liability fits |
| `fig_fan_charts.png` | Monte Carlo fan charts for all five strategies |
| `fig_projected_cashflow.png` | Median contribution vs. benefit projections |
| `fig_scenario_comparison.png` | Strategy comparison — median FR, P(≥80%), insolvency |
| `fig_historical_projection.png` | Historical 2001-2024 + projected 2024-2055 |
| `fig_stress_tests.png` | Stress test outcomes (median FR, insolvency risk) |
| `fig_counterfactual.png` | What if the city had always paid 100% required? |
| `fig_tornado.png` | Sensitivity tornado — which variables matter most |
| `fig_milestones.png` | Deterministic recovery milestones (50 / 65 / 80%) |

---

## Data source

The model expects a CSV exported from the
[Public Plans Database](https://publicplansdata.org/) filtered to
`PlanName == "Chicago (IL) Municipal"`.

Key columns used:

| Column | Description |
|--------|-------------|
| `fy` | Fiscal year |
| `ActLiabilities_GASB` | Actuarial liabilities (GASB) |
| `MktAssets_net` | Net market assets |
| `ActFundedRatio_GASB` | Actuarial funded ratio |
| `RequiredContribution` | Actuarially determined employer contribution |
| `PercentReqContPaid` | Fraction of required contribution actually paid |
| `InvestmentReturn_1yr` | 1-year net investment return |
| `EQTotal_Rtrn` | Equity total return |
| `FITotal_Rtrn` | Fixed-income total return |
| `beneficiaries_tot` | Total beneficiaries |
| `BeneficiaryBenefit_avg` | Average annual benefit |
| `actives_tot` | Total active members |
| `ActiveSalary_avg` | Average active salary |

---

## Key model assumptions

- **Simulation horizon**: 30 years (2025–2055), 10,000 paths
- **Asset returns**: Log-normal with Cholesky-correlated equity / fixed-income / alternatives; crisis-regime correlation matrix activates when funded ratio < 20%
- **Liability growth**: Historically calibrated, tapering from ~3.6% to 2.5% by 2050
- **Benefit payment growth**: Tapering from ~3.5% to 2.5% by 2050
- **Employer compliance**: Ramps toward cap over 2025-2027; shocked by bad return years
- **Employee contribution rate**: 8.5% of payroll
- **Administrative costs**: 0.5% of assets per year

---

## License

This project is provided for academic and competition purposes.
