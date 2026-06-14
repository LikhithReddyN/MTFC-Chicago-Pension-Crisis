def annuity(data):
    """
    Compute present value of annuity obligations.

    Uses three beneficiary cohorts (long-term, mid-term, near-term) with
    a 4.5% discount rate and 3% COLA, then applies a 12% market-rate markup.
    """
    nr = data["beneficiaries"][-1]
    ab = data["ben_avg"][-1]
    d = 0.045   # discount rate
    c = 0.03    # COLA

    # (fraction of beneficiaries, duration in years, benefit level)
    cohorts = [
        (0.40, 25, ab * 0.90),
        (0.35, 18, ab * 1.00),
        (0.25, 10, ab * 1.10),
    ]

    tpv = sum(
        nr * f * sum(b * (1 + c) ** t / (1 + d) ** t for t in range(1, T + 1))
        for f, T, b in cohorts
    )

    mk = 1.12
    pn = nr * 0.25
    ppv = sum(ab * 1.10 * (1 + c) ** t / (1 + d) ** t for t in range(1, 11))

    return {
        "full":      tpv * mk,
        "partial":   pn * ppv * mk,
        "shortfall": tpv * mk - data["assets"][-1],
    }
