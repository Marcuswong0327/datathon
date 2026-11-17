"""
UMDAC Datathon 2026 — Principal Insights & Reconstructed Causal Business Rules
Team: Plot Twists
Output: insights.pdf (12 slides: Page 1 Cover, Pages 2-11 Feature Groups 1-10, Page 12 Master Causal Graph & Methodology)
"""
import sys
import os
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

OUT = "insights.pdf"
NAVY, ORANGE, TEAL, RED, PURPLE, GREY = (
    "#1f4e79", "#e07b39", "#2a9d8f", "#c0392b", "#8e6bbf", "#7f8c8d"
)
INK, MUTED, PALE = "#1c2833", "#5d6d7e", "#eef3f8"
W, H = 13.333, 7.5
NS = 12

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#b0b8c1",
})


def chrome(fig, section, page):
    fig.add_artist(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color="white", zorder=-2))
    fig.add_artist(plt.Rectangle((0, 0.948), 1, 0.052, transform=fig.transFigure, color=NAVY, lw=0, zorder=2))
    fig.text(0.035, 0.974, section, color="white", fontsize=9.5, fontweight="bold", va="center")
    fig.text(0.965, 0.974, "UMDAC Datathon 2026  ·  Team: Plot Twists", color="white",
             fontsize=9.5, va="center", ha="right")
    # Footer text removed per user request; only clean page number on right
    fig.text(0.965, 0.026, f"{page}  /  {NS}", fontsize=8.5, color=MUTED, va="center", ha="right")


def wrap(text, width):
    return textwrap.wrap(text, width)


def para(fig, x, y, text, width, size=9.8, color=INK, weight="regular", lead=1.34):
    lines = wrap(text, width)
    fig.text(x, y, "\n".join(lines), fontsize=size, color=color, fontweight=weight,
             va="top", linespacing=lead, zorder=3)
    return y - len(lines) * (size * lead) / (H * 72) - 0.010


def new(section, page):
    fig = plt.figure(figsize=(W, H))
    chrome(fig, section, page)
    return fig


def save(pdf, fig):
    pdf.savefig(fig)
    plt.close(fig)


def ax_of(fig, rect):
    ax = fig.add_axes(rect)
    ax.tick_params(labelsize=7.6, colors=INK, length=3)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)
    return ax


def rule_block(fig, y, text, width=63):
    lines = wrap(text, width)
    line_h = (9.5 * 1.34) / (H * 72)
    h = len(lines) * line_h + 0.048
    fig.add_artist(plt.Rectangle((0.035, y - h), 0.48, h, transform=fig.transFigure,
                                 facecolor=PALE, edgecolor=NAVY, linewidth=0.9, zorder=1))
    fig.text(0.047, y - 0.015, "RECONSTRUCTED CAUSAL BUSINESS RULES", fontsize=8.0, color=NAVY,
             fontweight="bold", va="top", zorder=3)
    fig.text(0.047, y - 0.040, "\n".join(lines), fontsize=9.5, color=INK, va="top",
             linespacing=1.34, zorder=3)
    return y - h - 0.018


def economy(fig, y, text, width=63):
    fig.text(0.035, y, "REAL-WORLD ECONOMIC & LIVE-SYSTEM BEHAVIOUR", fontsize=8.0, color=TEAL,
             fontweight="bold", va="top")
    return para(fig, 0.035, y - 0.023, text, width, size=9.4, color=INK) - 0.008


def method_block(fig, y, text, width=63):
    fig.text(0.035, y, "METHODOLOGY & CAUSAL IDENTIFICATION", fontsize=8.0, color=ORANGE,
             fontweight="bold", va="top")
    return para(fig, 0.035, y - 0.023, text, width, size=9.2, color=MUTED)


def ref(fig, x, text):
    fig.text(x, 0.055, text, fontsize=7.8, color=MUTED, va="center", style="italic")


# ==============================================================================
# SLIDE 1: DEDICATED COVER PAGE (UMDAC Datathon 2026 · Team: Plot Twists)
# ==============================================================================
def s01_cover(pdf):
    fig = plt.figure(figsize=(W, H))
    fig.add_artist(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color=NAVY, zorder=-2))
    fig.add_artist(plt.Rectangle((0, 0.92), 1, 0.08, transform=fig.transFigure, color="#133352", lw=0, zorder=1))
    fig.add_artist(plt.Rectangle((0.04, 0.695), 0.92, 0.004, transform=fig.transFigure, color=ORANGE, lw=0, zorder=2))

    fig.text(0.04, 0.96, "UNIVERSITI MALAYA DATA ANALYTICS COMPETITION  ·  PRELIMINARY ROUND",
             color="#93c5fd", fontsize=10.5, fontweight="bold", va="center")
    fig.text(0.96, 0.96, "1  /  12", color="#93c5fd", fontsize=9.5, va="center", ha="right")

    fig.text(0.04, 0.865, "UMDAC Datathon 2026", color=ORANGE, fontsize=18.5, fontweight="bold", va="top")
    fig.text(0.04, 0.805, "Reverse-Engineering the Synthetic Swift Payment Book:\nCausal Business Rules, Latent Ciphers & Economic Mechanics",
             color="white", fontsize=18.2, fontweight="bold", va="top", linespacing=1.25)

    # Team Badge Box
    fig.add_artist(plt.Rectangle((0.70, 0.745), 0.26, 0.115, transform=fig.transFigure,
                                 facecolor="#133352", edgecolor=ORANGE, linewidth=1.6, zorder=2))
    fig.text(0.83, 0.832, "SUBMITTED BY GROUP", color="#93c5fd", fontsize=8.5, fontweight="bold", ha="center", va="center", zorder=3)
    fig.text(0.83, 0.785, "Plot Twists", color="white", fontsize=17.5, fontweight="bold", ha="center", va="center", zorder=3)

    fig.text(0.04, 0.665,
             "Complete structural reverse-engineering of 10,000,000 fictitious cross-border payments across 20 features.\n"
             "Pages 2–11 present the reconstructed business rules, supporting charts, live-market economic behaviour, and causal methodology\n"
             "for each of the 10 feature groups (matching dashboards.pdf Pages 1–10), followed by the Master Causal Graph on Page 12.",
             color="#e2e8f0", fontsize=10.2, va="top", linespacing=1.36)

    groups_left = [
        ("Slide 2  ·  Group 1: Data Quality & Scale", "Row-0 DISCLAIMER, 0% nulls, 6 anomaly classes & Days 19–30 payroll surge"),
        ("Slide 3  ·  Group 2: Time Patterns", "Universal 24h sender local-time curve, B (17:00) vs C (19:00) peaks & 88.8% weekday share"),
        ("Slide 4  ·  Group 3: Currency", "Path-weighted currency selection (20:1 B_0 weight) & 100.000% exact FX conversion identity"),
        ("Slide 5  ·  Group 4: Payment Value", "Exact +2.0 ln(USD) step per 'B' party, Sender GDP scaling & 38.69% local round rule"),
        ("Slide 6  ·  Group 5: Routing & Corridors", "BIC8 'BBBBCCLO' indexing, Zipf scaling & 100% Home Ordering vs 99% Global Beneficiary pool"),
    ]
    groups_right = [
        ("Slide 7  ·  Group 6: Path Structure", "Euler 1/e (0.3679) geometric hop decay, 88.7/11.3 split & 5.0%/hop '...' / boundary dropout"),
        ("Slide 8  ·  Group 7: Duration", "Directed-Edge Additive Latency Law (R² = 0.9982), bimodal corridors & 45x cover speedup"),
        ("Slide 9  ·  Group 8: Party Types", "Independent Bernoulli sampling (78.75% B Ord × 28.82% B Ben) & product/country invariance"),
        ("Slide 10 ·  Group 9: Accounts & Tokens", "6-digit PARTY_ID tail cipher, 100% B/C token exclusivity & MT103 50K/50F/50A templates"),
        ("Slide 11 ·  Group 10: Anomaly Labels", "Shared 1,068-mule syndicate pool, Fat-Finger ×10^k, 185 Dupes & CUSTOMER_RECALL KS null proof"),
    ]

    for idx, (g_title, g_sub) in enumerate(groups_left):
        y_pos = 0.49 - idx * 0.084
        fig.add_artist(plt.Rectangle((0.04, y_pos - 0.055), 0.44, 0.068, transform=fig.transFigure,
                                     facecolor="#163a5f", edgecolor="#335c85", linewidth=0.8, zorder=2))
        fig.text(0.055, y_pos - 0.005, g_title, color=ORANGE, fontsize=9.6, fontweight="bold", va="top", zorder=3)
        fig.text(0.055, y_pos - 0.032, g_sub, color="#cbd5e1", fontsize=8.1, va="top", zorder=3)

    for idx, (g_title, g_sub) in enumerate(groups_right):
        y_pos = 0.49 - idx * 0.084
        fig.add_artist(plt.Rectangle((0.52, y_pos - 0.055), 0.44, 0.068, transform=fig.transFigure,
                                     facecolor="#163a5f", edgecolor="#335c85", linewidth=0.8, zorder=2))
        fig.text(0.535, y_pos - 0.005, g_title, color="#38bdf8", fontsize=9.6, fontweight="bold", va="top", zorder=3)
        fig.text(0.535, y_pos - 0.032, g_sub, color="#cbd5e1", fontsize=8.1, va="top", zorder=3)

    fig.text(0.04, 0.042, "Slide 12  ·  Master Causal DAG, Operational Screening Blueprint & Analytical Limits",
             color="#93c5fd", fontsize=9.5, fontweight="bold")
    save(pdf, fig)


# ==============================================================================
# SLIDE 2: FEATURE GROUP 1 — DATA QUALITY AND SCALE
# ==============================================================================
def s02_group1(pdf):
    fig = new("Feature group 1  ·  Data quality and scale", 2)
    fig.text(0.035, 0.905, "Complete 10M-row synthetic book, 6 anomaly classes, and an end-of-month surge",
             fontsize=16.5, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Hidden Row-0 Blueprint: Row 0 contains an undocumented 21st column (DISCLAIMER) stating the book was generated exclusively via hard-coded rules, NumPy random draws, and Python Faker.\n"
        "2. Population Integrity: Across all 10,000,000 retained rows (30 Apr 2023 11:22 UTC to 31 Jul 2023 09:56 UTC), timestamp, USD amount, BIC path, and party details have 0.00% nulls, USD_AMOUNT > 0 everywhere, and exact row duplicates are 1 in 10M.\n"
        "3. Anomaly Rarity & Monthly Surge: ANOMALY_TYPE is populated on 7,006 rows (0.0701%) across 6 classes (including undocumented CUSTOMER_RECALL, n=317). Daily volume surges +55% across Days 19–30 (peaking on Day 26 at 4.91%).")
    y = economy(fig, y,
        "A live monitoring team can treat the dataset as a clean, complete ledger without broken records or missing mandatory MT103 fields. "
        "Any fraud/error detector must operate at a 1-in-1,427 base rate (0.070%) while accommodating a 55% end-of-month corporate payroll and accounts-payable settlement surge during the final 12 days of each month.")
    method_block(fig, y,
        "Out-of-core full-population scan inspected raw CSV headers/row 0 (uncovering the 21st DISCLAIMER column), verified exact null rates, distinct row hashes, and positivity constraints across all 10,000,000 records, and decomposed daily volume into weekly and day-of-month (1..31) components.")

    a = pd.read_csv("agg/d1_anom.csv")
    names = {"NONE": "Unlabelled", "ROMANCE_SCAM": "Romance", "FAT_FINGER_MISTAKE": "Fat finger",
             "CEO_SCAM": "CEO", "DUPLICATE_PAYMENT": "Duplicate",
             "ACCOUNT_REPLACEMENT_SCAM": "Acct replace.", "CUSTOMER_RECALL": "Cust. recall*"}
    a["label"] = a["a"].map(names).fillna(a["a"])
    ax1 = ax_of(fig, [0.62, 0.54, 0.34, 0.30])
    ax1.barh(a["label"][::-1], a["n"].to_numpy()[::-1], color=ORANGE, height=0.68)
    ax1.set_xscale("log")
    ax1.set_xlim(100, 5e7)
    ax1.set_xlabel("Payments (log scale)")
    ax1.set_title("A. Label counts across 10M rows (*6th class)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")
    for idx, val in enumerate(a["n"].to_numpy()[::-1]):
        ax1.text(val * 1.15, idx, f"{int(val):,}", va="center", fontsize=7.2, fontweight="bold")

    dom = pd.read_csv("agg/d1_dom.csv")
    ax2 = ax_of(fig, [0.62, 0.14, 0.34, 0.30])
    cols_d = [NAVY if d < 19 else ORANGE if d != 26 else RED for d in dom["dom"]]
    ax2.bar(dom["dom"], dom["share_pct"], color=cols_d, width=0.75)
    ax2.axhline(100 / 30.67, color=TEAL, linestyle="--", lw=1.2, label="Uniform daily share (3.26%)")
    ax2.set_ylim(0, 5.6)
    ax2.set_xlabel("Day of calendar month (1..31)")
    ax2.set_ylabel("Monthly share (%)")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax2.set_title("B. End-of-month surge (Days 19–30; Day 26 = 4.91%)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")

    ref(fig, 0.62, "Supporting charts: dashboards.pdf, Page 1.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 3: FEATURE GROUP 2 — TIME PATTERNS
# ==============================================================================
def s03_group2(pdf):
    fig = new("Feature group 2  ·  Time patterns", 3)
    fig.text(0.035, 0.905, "Every country follows one universal 24-hour curve in the sender's local timezone",
             fontsize=16.5, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Universal Local-Time Circadian Law: Shifting UTC hour by the Ordering Country's UTC offset (H_local = (H_UTC + TZ_OFFSET(ORD_COUNTRY)) mod 24) collapses all countries onto ONE identical 24-hour curve: nighttime trough 01:00–06:00 (~0.95%/hr), morning opening spike at 08:00 local (7.60%), and lunch dip at 12:00 (4.25%).\n"
        "2. Party-Specific Evening Peak: Businesses ('B') peak at 17:00–19:00 local (7.6%, treasury cutoff), whereas Consumers ('C') peak 2 hours later at 19:00 local (8.2%, evening retail banking).\n"
        "3. Weekly Cycle & Flat Anomaly Rate: Mon–Fri carry 88.82% of volume (1.70M–1.83M/day) vs Sat (0.435M) and Sun (0.684M). Anomaly rate is invariant across UTC hours (0.056%–0.089%).")
    y = economy(fig, y,
        "Domestic RTGS clearing systems (Fedwire, TARGET2, CHAPS, CNAPS) open around 08:00 local time and enforce corporate treasury cutoffs at 17:00–18:00 local time, while retail consumers submit remittances after work (~19:00 local). "
        "Because anomaly injection is independent of timestamp, off-hours screening provides zero fraud lift over daytime screening.")
    method_block(fig, y,
        "Computed UTC hourly distributions per Ordering Country (CN peak 00:00/08:00 UTC, DE/FR/CH 06:00/15:00–17:00 UTC, GB 07:00/18:00 UTC, US 12:00/23:00 UTC) and aligned each by its May–July 2023 UTC offset (+8, +2, +1, -4), proving exact curve invariance across jurisdictions.")

    hc = pd.read_csv("agg/d2_hour_by_country.csv")
    ax1 = ax_of(fig, [0.58, 0.54, 0.38, 0.30])
    colors = {"US": NAVY, "GB": ORANGE, "DE": TEAL, "FR": RED, "CH": PURPLE, "SG": GREY}
    for oc, g in hc.groupby("oc"):
        g = g.sort_values("hr")
        ax1.plot(g["hr"], 100 * g["n"] / g["n"].sum(), color=colors.get(oc, INK), lw=1.6, label=oc)
    ax1.set_xlim(0, 23); ax1.set_ylim(0, 8.8)
    ax1.set_ylabel("Share (%)")
    ax1.legend(ncol=6, fontsize=7.5, frameon=False, loc="upper center")
    ax1.set_title("A. Raw UTC hour profile by sending country (phase-shifted)", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    lh = pd.read_csv("agg/d2_local_hour.csv")
    ax2 = ax_of(fig, [0.58, 0.14, 0.38, 0.30])
    for c in ["US", "GB", "DE", "CN", "JP"]:
        ax2.plot(lh["local_hr"], lh[f"{c}_local_pct"], alpha=0.35, lw=1.1, linestyle="--")
    ax2.plot(lh["local_hr"], lh["B_share_pct"], color=NAVY, lw=2.2, marker="o", markersize=3.5, label="Business 'B' (17:00 peak, 7.6%)")
    ax2.plot(lh["local_hr"], lh["C_share_pct"], color=RED, lw=2.2, marker="s", markersize=3.5, label="Consumer 'C' (19:00 peak, 8.2%)")
    ax2.set_xlim(0, 23); ax2.set_ylim(0, 9.2)
    ax2.set_xlabel("Sender Local Hour: (H_UTC + TZ_OFFSET) mod 24")
    ax2.set_ylabel("Share (%)")
    ax2.legend(frameon=False, fontsize=7.8, loc="upper left")
    ax2.set_title("B. Universal collapse in local time & B vs C evening peaks", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    ref(fig, 0.58, "Supporting charts: dashboards.pdf, Page 2.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 4: FEATURE GROUP 3 — CURRENCY
# ==============================================================================
def s04_group3(pdf):
    fig = new("Feature group 3  ·  Currency", 4)
    fig.text(0.035, 0.905, "Path-weighted currency selection (20:1 sender weight) and the 100% FX hop identity",
             fontsize=16.5, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Path-Weighted Currency Selection (20:1 Weight on B_0): On 98.77% of complete paths, CURRENCY_CODE is drawn from the native currencies of the banks in BIC8_PATH, with Ordering Bank B_0 weighted ~20:1 against each subsequent bank B_1..B_{K-1} (95.6% B_0 at K=2; 92.1% B_0 at K=3). Only 1.23% use an offshore vehicle currency.\n"
        "2. Home Currency Dominance: Consequently, 86%–95% of payments use the sender's domestic currency (DE 94.5% EUR, FR 94.0% EUR, US 90.5% USD, CH 88.8% CHF, GB 88.6% GBP, SG 87.5% SGD, CN 86.2% CNY).\n"
        "3. 100.000% Exact FX Conversion Identity: CURRENCY_CONVERSION_COUNT = sum_{i=1}^{K-1} I(NativeCurr(B_i) != NativeCurr(B_{i+1})) with 0 errors across 30,000 continuous paths — explaining why 36.9% of domestic-endpoint payments convert currency when routed via foreign intermediaries.")
    y = economy(fig, y,
        "Senders overwhelmingly denominate payment instructions in their local funding currency, leaving cross-currency conversion to correspondent banks along the route. "
        "Even when sender and beneficiary reside in the same country, routing through an international clearing hub (e.g., USD or EUR cover bank) triggers two back-to-back FX conversions along the chain.")
    method_block(fig, y,
        "Conditioned CURRENCY_CODE on complete paths where all K banks have distinct native currencies to isolate the exact 20:1 selection weights, and tested the adjacent country-currency transition sum against CURRENCY_CONVERSION_COUNT (100.000% match).")

    rows = [("DE", "EUR", 94.5), ("FR", "EUR", 94.0), ("IT", "EUR", 93.3), ("US", "USD", 90.5),
            ("CH", "CHF", 88.8), ("GB", "GBP", 88.6), ("SG", "SGD", 87.5), ("CN", "CNY", 86.2)]
    ax1 = ax_of(fig, [0.60, 0.54, 0.36, 0.30])
    labels = [f"{a} ({b})" for a, b, _ in rows][::-1]
    vals = [v for _, _, v in rows][::-1]
    ax1.barh(labels, vals, color=NAVY, height=0.68)
    ax1.set_xlim(0, 108)
    ax1.set_xlabel("Share of sender country payments (%)")
    ax1.set_title("A. Home currency share across top sending countries", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")
    for i, v in enumerate(vals):
        ax1.text(v + 1.2, i, f"{v:.1f}%", va="center", fontsize=7.8, fontweight="bold")

    pw = pd.read_csv("agg/d3_path_curr_weights.csv")
    ax2 = ax_of(fig, [0.60, 0.14, 0.36, 0.30])
    x = np.arange(len(pw))
    ax2.bar(x, pw["b0_ord_pct"], width=0.50, color=NAVY, label="First Bank B_0 (Ordering, Weight ~20)")
    ax2.bar(x, pw["b_interm_pct"], bottom=pw["b0_ord_pct"], width=0.50, color=ORANGE, label="Intermediary B_1..B_{K-2} (Weight 1 ea.)")
    ax2.bar(x, pw["b_last_ben_pct"], bottom=pw["b0_ord_pct"] + pw["b_interm_pct"], width=0.50, color=TEAL, label="Last Bank B_{K-1} (Beneficiary, Weight 1)")
    ax2.set_xticks(x); ax2.set_xticklabels([f"K = {k} Banks" for k in pw["k"]])
    ax2.set_ylim(0, 108)
    ax2.set_ylabel("Share (%)")
    ax2.legend(frameon=False, fontsize=7.2, loc="lower left")
    ax2.set_title("B. Which bank in BIC8_PATH sets CURRENCY_CODE?", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    ref(fig, 0.60, "Supporting charts: dashboards.pdf, Page 3.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 5: FEATURE GROUP 4 — PAYMENT VALUE
# ==============================================================================
def s05_group4(pdf):
    fig = new("Feature group 4  ·  Payment value", 5)
    fig.text(0.035, 0.905, "Exact +2.0 natural-log step per Business party, GDP scaling, and 38.7% round amounts",
             fontsize=16.2, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Exact +2.0 Natural-Log Party-Type Law: ln(USD_AMOUNT) ~ Normal(mu_pair + delta_GDP(ORD_COUNTRY), sigma_ln^2) with constant sigma_log10 = 1.00, where mu_ln steps up by EXACTLY +2.0 (e^2 = 7.39x in USD) per Business ('B') participant: C->C mu_ln = 6.00 (med USD 463) | B->C & C->B mu_ln = 8.00 (med USD 3,119 / USD 3,229) | B->B mu_ln = 10.00 (med USD 22,888).\n"
        "2. Ordering Country GDP-per-Capita Scaling: Mean log10(USD) scales linearly with Ordering Country GDP per capita (SD = 0.457 across sender countries: MC 4.43, LU 3.97, US 3.77 vs IN 2.38, VN 2.35) and has ZERO causal dependence on Beneficiary Country (SD = 0.056).\n"
        "3. 38.69% Round Local-Currency Rule & Daily FX Table: 38.69% of payments are generated as exact round denominations (100, 500, 1k, 5k, 10k, 100k) in local CURRENCY_CODE and multiplied by a daily exchange rate FX(currency, date).")
    y = economy(fig, y,
        "Retail peer-to-peer remittances (~USD 463), commercial salary/invoice payouts (~USD 3,150), and wholesale B2B trade settlements (~USD 22,888) sit separated by uniform multiplicative steps (e^2 = 7.39x). "
        "Transaction sizes scale with the macroeconomic purchasing power (GDP per capita) of the originating economy, while human contract conventions produce sharp clusters at round local-currency denominations.")
    method_block(fig, y,
        "Performed two-way fixed-effects variance decomposition across (ORD_COUNTRY × BEN_COUNTRY × Party_Pair), proving an 8.2x dispersion ratio between Sender Country (SD=0.457) and Receiver Country (SD=0.056), and extracted daily FX rates from same-day USD_AMOUNT ratios.")

    pd_df = pd.read_csv("agg/d4_party_densities.csv")
    ax1 = ax_of(fig, [0.58, 0.54, 0.38, 0.30])
    xb = pd_df["log10_usd"]
    for col, lbl, col_c in [
        ("CC_density", "C->C (μ_ln=6.0, USD 463)", RED),
        ("BC_density", "B->C (μ_ln=8.0, USD 3,119)", ORANGE),
        ("CB_density", "C->B (μ_ln=8.0, USD 3,229)", TEAL),
        ("BB_density", "B->B (μ_ln=10.0, USD 22,888)", NAVY),
    ]:
        ax1.plot(xb, pd_df[col], color=col_c, lw=2.0, label=lbl)
        ax1.fill_between(xb, pd_df[col], color=col_c, alpha=0.10)
    ax1.set_xlabel("log10(USD_AMOUNT)")
    ax1.set_ylabel("Density")
    ax1.legend(frameon=False, fontsize=7.2, loc="upper right")
    ax1.set_title("A. Exact +2.0 ln(USD) step per Business ('B') party", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    gdp = pd.read_csv("agg/d4_country_gdp.csv").iloc[::2].iloc[::-1]
    ax2 = ax_of(fig, [0.58, 0.14, 0.38, 0.30])
    ax2.barh(gdp["country"], gdp["mean_log10_usd"], color=NAVY, height=0.68)
    ax2.set_xlim(0, 5.5)
    ax2.set_xlabel("Mean log10(USD_AMOUNT) by Ordering Country")
    ax2.set_title("B. Sender GDP-per-capita scaling (Sender SD=0.457 vs Ben SD=0.056)", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")
    for i, v in enumerate(gdp["mean_log10_usd"]):
        ax2.text(v + 0.06, i, f"{v:.2f} (USD {10**v:,.0f})", va="center", fontsize=7.5, fontweight="bold")

    ref(fig, 0.58, "Supporting charts: dashboards.pdf, Page 4.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 6: FEATURE GROUP 5 — ROUTING AND CORRIDORS
# ==============================================================================
def s06_group5(pdf):
    fig = new("Feature group 5  ·  Routing and corridors", 6)
    fig.text(0.035, 0.905, "BIC8 sequential indexing, Zipf hub scaling, and 100% home vs 99% offshore banking",
             fontsize=16.2, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. BIC8 Naming Rule ('BBBBCCLO'): Characters 0..3 (BBBB) are a 0-indexed sequential bank ID within country CC (0000..1135 for 1,136 US banks; 0000..0677 for 678 GB banks; 0000..0636 for 637 DE banks), char 6 (L) is the city code ('3'=NY, '2'=London), and char 7 is '0'.\n"
        "2. Zipf Hub Concentration: Across 26,764 corridors, country volume scales as a power law of its bank pool size. US->US is the largest corridor (385,598 rows, 3.86%); top 15 corridors capture 16.1%; top bank pair 0001MQM0->0009TNT0 repeats 20,005 times.\n"
        "3. 100% Home Ordering vs 99% Offshore Beneficiary Pool: Ordering parties bank 100.0% in their residential country (ORD_BIC8[4:6] == ORD_TOKENS country), whereas Beneficiary BICs are drawn independently across the global bank pool (0.98% address match; domestic bank share = P(BEN_C = c): 24.3% in US, <10% elsewhere).")
    y = economy(fig, y,
        "Senders initiate wires from their domestic relationship bank (100% home match), whereas multinational beneficiaries, exporters, and treasury centers receive funds across global settlement hubs (especially the United States, Switzerland, and Britain). "
        "Because US banks represent ~24% of the beneficiary pool, ~24% of US-originated wires settle domestically inside the US while smaller countries settle >90% cross-border.")
    method_block(fig, y,
        "Parsed all 8,392 ORDERING_BIC8 and 8,266 BENEFICIARY_BIC8 strings to verify 0..N-1 sequential indexing per country, regressed log country volume on log bank count, and cross-tabulated <country_code:XX> tokens against BIC8[4:6].")

    cor = pd.read_csv("agg/d5_corridors.csv")
    cor["k"] = cor["oc"] + " → " + cor["bc"]
    top = cor.nlargest(8, "n").iloc[::-1]
    ax1 = ax_of(fig, [0.58, 0.54, 0.38, 0.30])
    ax1.barh(top["k"], top["n"].to_numpy() / 1e3, color=ORANGE, height=0.68)
    ax1.set_xlabel("Payments (thousands)")
    ax1.set_title("A. Eight largest corridors across 26,764 country pairs", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    zf = pd.read_csv("agg/d5_country_zipf.csv")
    ax2 = ax_of(fig, [0.58, 0.14, 0.38, 0.30])
    ax2.scatter(zf["n_banks"], zf["vol"], color=PURPLE, edgecolors=NAVY, alpha=0.75, s=32)
    ax2.set_xscale("log"); ax2.set_yscale("log")
    m_sl, b_in = np.polyfit(np.log10(zf["n_banks"]), np.log10(zf["vol"]), 1)
    xl = np.logspace(0, 3.1, 50)
    ax2.plot(xl, (10**b_in) * (xl**m_sl), color=RED, linestyle="--", lw=1.8, label=f"Power-law fit (slope={m_sl:.2f})")
    for c_lbl in ["US", "GB", "DE", "CH", "CN", "SG"]:
        sub = zf[zf["country"] == c_lbl]
        if not sub.empty:
            ax2.annotate(c_lbl, (sub["n_banks"].values[0], sub["vol"].values[0]), xytext=(4, 2), textcoords="offset points", fontsize=7.5, fontweight="bold")
    ax2.set_xlabel("Active banks in country ('0000'..'N-1') [log]")
    ax2.set_ylabel("Sample volume [log]")
    ax2.legend(frameon=False, fontsize=7.8, loc="upper left")
    ax2.set_title("B. Country bank pool size vs payment volume (100% Home Ord)", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    ref(fig, 0.58, "Supporting charts: dashboards.pdf, Page 5.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 7: FEATURE GROUP 6 — PATH STRUCTURE
# ==============================================================================
def s07_group6(pdf):
    fig = new("Feature group 6  ·  Path structure", 7)
    fig.text(0.035, 0.905, "Euler (1/e) geometric hop decay, constant 88.7/11.3 split, and 5% per-hop dropout",
             fontsize=16.2, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Shifted Geometric Hop Decay with Exact Euler Ratio (1/e = 0.3679): Observable bank count K = PARTICIPANT_COUNT (K >= 2) follows P(K = k) = (1 - 1/e)*(1/e)^(k-2): observed P(K=2) = 63.2328% vs theoretical 1 - 1/e = 63.2121%, with constant step decay ratio P(K+1)/P(K) = 0.3676 across all K.\n"
        "2. Deterministic & Constant Product Split: K == 2 maps 100.0% to 'Direct' (6,323,280 rows). Every K >= 3 splits at an invariant ratio of 88.69% 'Indirect' (3,260,758 rows) vs 11.31% 'Covered' (415,962 rows).\n"
        "3. The 5.0% Per-Hop Dropout Law: Each hop along the path drops out of visibility with p = 5.0%: internal drops insert '...' and set CONTINUITY_QFLAG = 'N' (767,204 rows, 7.672%, 0 disagreements), while boundary drops create unflagged 5.0% endpoint mismatches (BIC8_PATH[:8] != ORD_BIC8 in 4.99%, BIC8_PATH[-8:] != BEN_BIC8 in 4.95% where QFLAG stays 'Y'!).")
    y = economy(fig, y,
        "When two banks lack a direct bilateral account (36.77% of wires), they route either serially through intermediary banks (Indirect MT103 chain, 88.7%) or via a separate reimbursement cover path (Covered MT103 + MT202 COV, 11.3%). "
        "Non-reporting intermediary hops create internal tracker gaps ('...', QFLAG='N'), whereas an unreported first or last leg truncates the path endpoint without triggering an internal gap flag.")
    method_block(fig, y,
        "Regressed log P(PARTICIPANT_COUNT = K) on K (recovering exact natural-log slope -1.000 => 1/e), verified 100% equivalence between '...' and QFLAG='N', and tested endpoint equality BIC8_PATH[:8]==ORD_BIC8 and BIC8_PATH[-8:]==BEN_BIC8.")

    eu = pd.read_csv("agg/d6_euler_decay.csv")
    ax1 = ax_of(fig, [0.62, 0.54, 0.34, 0.30])
    ax1.semilogy(eu["k"], eu["obs_pct"], "o-", color=NAVY, lw=2.2, markersize=5.5, label="Observed share (%)")
    ax1.semilogy(eu["k"], eu["euler_theo_pct"], "s--", color=RED, lw=1.8, markersize=4.5, label="Exact Euler law: (1-1/e)·(1/e)^(K-2)")
    ax1.set_xlabel("PARTICIPANT_COUNT (K observable banks)")
    ax1.set_ylabel("Share (%) [log]")
    ax1.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax1.set_title("A. Exact 1/e (0.3679) geometric decay of participant count", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")

    tr = pd.read_csv("agg/d6_truncations.csv").iloc[::-1]
    ax2 = ax_of(fig, [0.62, 0.14, 0.34, 0.30])
    short_m = ["Both ends\n(0.05²=0.25%)", "Last != BEN\n(QFLAG='Y')", "First != ORD\n(QFLAG='Y')", "Internal '...'\n(QFLAG='N')"]
    ax2.barh(short_m, tr["rate_pct"], color=[PURPLE, ORANGE, ORANGE, RED], height=0.62)
    ax2.set_xlim(0, 9.5)
    ax2.set_xlabel("Occurrence rate across 10,000,000 rows (%)")
    ax2.set_title("B. 5.0%/hop dropout: '...' vs unflagged end truncations", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")
    for i, v in enumerate(tr["rate_pct"]):
        ax2.text(v + 0.15, i, f"{v:.2f}%", va="center", fontsize=7.8, fontweight="bold")

    ref(fig, 0.62, "Supporting charts: dashboards.pdf, Page 6.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 8: FEATURE GROUP 7 — DURATION
# ==============================================================================
def s08_group7(pdf):
    fig = new("Feature group 7  ·  Duration", 8)
    fig.text(0.035, 0.905, "The R² = 0.9982 Directed-Edge Additive Latency Law and the 45x cover speedup",
             fontsize=16.5, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Bimodal Directed-Edge Latency Matrix L(B_i -> B_{i+1}): Every ordered bank pair has a fixed intrinsic latency L(B_i -> B_{i+1}) (within-edge SD ~ 6.8s) drawn from two regimes: ~73% Fast STP edges (9.5s–25s; Direct median = 39s) vs ~27% Slow Manual/Batch edges (100s–8,215s).\n"
        "2. Exact Multi-Hop Additive Latency Law (R² = 0.998212): For any complete path [B_1, B_2, ..., B_K], total duration is strictly the sum of its directed edge latencies minus a constant 17.0s endpoint overhead per intermediary: TOTAL_DURATION = sum_{i=1}^{K-1} L(B_i -> B_{i+1}) - 17.0*(K - 2) + eps.\n"
        "3. Chain Length vs Cover Speedup Paradox: Across the whole book, median duration rises with K (39s at K=2, 126s at K=3, 418s at K=4, 2,171s at K=12; Indirect med 281s, Covered 383s; Gap '...' med 155s vs Continuous 54s). Yet for a slow direct edge (0219US30->0159US30, 424.1s), routing via two fast cover STP edges settles in 9.4s (45x faster)!")
    y = economy(fig, y,
        "In live correspondent banking, bilateral links without automated STP or pre-funded liquidity require manual repair or batch queuing (~20+ minutes). "
        "Routing through a major clearing intermediary replaces one slow bilateral link with two automated STP hops, settling in under 10 seconds.")
    method_block(fig, y,
        "Estimated mean edge latency L(B_i -> B_j) exclusively from 2-bank Direct paths, then predicted 3-bank path duration out-of-sample as L(B1->B2) + L(B2->B3) - 17.0s across 7,395 paths, achieving R² = 0.998212.")

    sc = pd.read_csv("agg/d7_edge_latency_scatter.csv")
    ax1 = ax_of(fig, [0.58, 0.54, 0.38, 0.30])
    ax1.scatter(sc["pred_dur"], sc["actual_dur"], color=NAVY, alpha=0.65, s=22, label="3-Bank paths (B1→B2→B3)")
    mv = max(sc["pred_dur"].max(), sc["actual_dur"].max())
    ax1.plot([0, mv], [0, mv], "r--", lw=1.8, label="Exact 1:1 line (R² = 0.998212)")
    ax1.set_xlabel("Predicted: L(B1→B2) + L(B2→B3) - 17.0s (sec)")
    ax1.set_ylabel("Observed duration (sec)")
    ax1.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax1.set_title("A. Out-of-sample proof of Additive Edge Latency Law", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    part = pd.read_csv("agg/d7_part.csv")
    part = part[part["part"].between(2, 12)]
    ax2 = ax_of(fig, [0.58, 0.14, 0.38, 0.30])
    ax2.plot(part["part"], part["med"], color=NAVY, marker="o", lw=2, markersize=4.5, label="Median duration (s)")
    ax2.plot(part["part"], part["p90"], color=ORANGE, marker="s", lw=1.6, markersize=4.5, label="90th percentile (s)")
    ax2.set_xlabel("PARTICIPANT_COUNT (K banks on path)")
    ax2.set_ylabel("Seconds")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax2.set_title("B. Median and P90 duration across chain length K = 2..12", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    ref(fig, 0.58, "Supporting charts: dashboards.pdf, Page 7.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 9: FEATURE GROUP 8 — PARTY TYPES
# ==============================================================================
def s09_group8(pdf):
    fig = new("Feature group 8  ·  Party types", 9)
    fig.text(0.035, 0.905, "Independent Bernoulli counterparty sampling (78.8% B × 28.8% B) and e² value steps",
             fontsize=16.2, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Strict Statistical Independence of Party Types: ORDERING_TYPE ~ Bernoulli(p_B = 78.75%) and BENEFICIARY_TYPE ~ Bernoulli(p_B = 28.82%) are drawn independently (Chi-square p = 0.89; joint counts match P(Ord)*P(Ben) to within 0.01% across 10M rows):\n"
        "   • B -> C: 5,603,692 rows (56.04% obs vs 56.05% theo), median USD 3,119\n"
        "   • B -> B: 2,270,945 rows (22.71% obs vs 22.70% theo), median USD 22,888\n"
        "   • C -> C: 1,514,758 rows (15.15% obs vs 15.13% theo), median USD 463\n"
        "   • C -> B:   610,605 rows ( 6.11% obs vs  6.12% theo), median USD 3,229\n"
        "2. Product & Corridor Invariance: Business sender share is identical across Direct, Indirect, and Covered routing (78.8% B) and stays within 75%–86% across all major countries.")
    y = economy(fig, y,
        "Corporates ('B') originate nearly four-fifths of payment instructions (global payroll, supplier invoices, benefits, and wholesale trade), while individuals ('C') are the majority recipients (71.2%) because B2C payroll/disbursements (56.0% of the book) outnumber B2B invoices (22.7%) by 2.5 to 1. "
        "Each Business participant multiplies the median payment value by e^2 = 7.39x (USD 463 -> USD 3,150 -> USD 22,888).")
    method_block(fig, y,
        "Constructed the full 2×2 contingency table on all 10,000,000 rows, tested independence against the product of marginals P(Ord_B)=0.78746 and P(Ben_B)=0.28815, and checked conditional invariance across TRANSACTION_TYPE_CODE and ORD_COUNTRY.")

    m = pd.read_csv("agg/d8_types.csv")
    m["k"] = m["oty"] + " → " + m["bty"]
    order = ["B → C", "B → B", "C → C", "C → B"]
    m = m.set_index("k").loc[order]
    obs_pct = (m["n"] / m["n"].sum()) * 100
    theo_pct = [56.05, 22.70, 15.13, 6.12]

    ax1 = ax_of(fig, [0.58, 0.54, 0.38, 0.30])
    x = np.arange(4)
    ax1.bar(x - 0.18, obs_pct, width=0.35, color=NAVY, label="Observed share (%)")
    ax1.bar(x + 0.18, theo_pct, width=0.35, color=ORANGE, label="Independent product P(Ord)·P(Ben)")
    ax1.set_xticks(x); ax1.set_xticklabels(order, fontweight="bold")
    ax1.set_ylim(0, 66)
    ax1.set_ylabel("Share of book (%)")
    ax1.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax1.set_title("A. Observed vs independent theoretical party-type shares", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")

    ax2 = ax_of(fig, [0.58, 0.14, 0.38, 0.30])
    order_med = ["B → B", "C → B", "B → C", "C → C"]
    m_med = m.loc[order_med]
    bars = ax2.bar(order_med, m_med["med"], color=[NAVY, TEAL, ORANGE, RED], width=0.62)
    ax2.set_ylim(0, 27500)
    ax2.set_ylabel("Median USD")
    ax2.set_title("B. Median USD by pair (7.39x step per Business participant)", loc="left", fontsize=9.8, color=NAVY, fontweight="bold")
    for b_bar, v in zip(bars, m_med["med"]):
        ax2.text(b_bar.get_x() + b_bar.get_width() / 2, v + 500, f"USD {v:,.0f}", ha="center", fontsize=8.0, fontweight="bold")

    ref(fig, 0.58, "Supporting charts: dashboards.pdf, Page 8.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 10: FEATURE GROUP 9 — ACCOUNTS AND TOKENS
# ==============================================================================
def s10_group9(pdf):
    fig = new("Feature group 9  ·  Party details and accounts", 10)
    fig.text(0.035, 0.905, "The 6-digit PARTY_ID cipher, 100% B/C token exclusivity, and MT103 field templates",
             fontsize=16.2, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. The 6-Digit PARTY_ID Cipher: Every underlying person/company has a permanent 6-digit PARTY_ID = re.sub('\\D','',account)[-6:] embedded at the end of their _FAKE_ account across all banks (e.g., IBAN '_FAKE_<CC><check><BankID>00000000<PARTY_ID>' on 91%–96% of European wires vs 0% in US/SG/CN/HK/JP/AU).\n"
        "2. Heavy-Tailed Account Reuse: Across 391,132 ordering accounts, 33% send once, median is 3, max is 75,803, and the top 1% originate 46% of all payments. Across 2.59M beneficiary accounts, 78% receive a single payment.\n"
        "3. 100% Token Exclusivity & 3 MT103 Templates: <business:N> (85.5%) and <company_keyword:N> (26.5%) occur 100.0% in 'B'; <first_name:N> (57.8%) and <last_name:N> (86.1%) occur 100.0% in 'C'. Details follow 83.3% MT103 50K (<line_break:35> wrap), 15.0% 50F ('1/ 2/ 3/'), 1.4% 50A, plus 9.3% '//' prefix.")
    y = economy(fig, y,
        "In live SWIFT FIN MT103 traffic, Field 50K/59 enforces a legacy 4×35-character line wrap (<line_break:35>), Field 50F uses structured '1/ 2/ 3/' subfields, and European banks mandate ISO 13616 IBANs while US/APAC rails use domestic BBANs. "
        "De-anonymizing the 6-digit PARTY_ID resolves multi-bank entities across all 2.59 million beneficiary accounts.")
    method_block(fig, y,
        "Grouped identical BENEFICIARY_DETAILS across distinct BENEFICIARY_BIC8 banks to uncover the invariant 6-digit tail cipher and 4-digit bank prefix, and cross-tabulated all <tag:N> tokens against ORDERING_TYPE and BENEFICIARY_TYPE.")

    te = pd.read_csv("agg/d9_token_exclusivity.csv").iloc[::-1]
    ax1 = ax_of(fig, [0.62, 0.54, 0.34, 0.30])
    y_idx = np.arange(len(te))
    ax1.barh(y_idx + 0.18, te["B_rate_pct"], height=0.35, color=NAVY, label="Business ('B') rate (%)")
    ax1.barh(y_idx - 0.18, te["C_rate_pct"], height=0.35, color=TEAL, label="Consumer ('C') rate (%)")
    ax1.set_yticks(y_idx); ax1.set_yticklabels(te["token"], family="monospace", fontsize=7.8, fontweight="bold")
    ax1.set_xlim(0, 108)
    ax1.set_xlabel("Token presence rate (%)")
    ax1.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax1.set_title("A. 100% deterministic token exclusivity (B vs C)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")

    labels = ["US", "CH", "GB", "FR", "DE", "SG", "CN", "HK"]
    iban = [0, 92.4, 92.0, 92.1, 92.1, 0, 0, 0]
    detail = [72.6, 98.8, 97.7, 99.6, 98.7, 66.7, 68.2, 77.6]
    ax2 = ax_of(fig, [0.62, 0.14, 0.34, 0.30])
    x = np.arange(len(labels))
    ax2.bar(x - 0.18, iban, width=0.36, color=NAVY, label="IBAN token (<iban:22>)")
    ax2.bar(x + 0.18, detail, width=0.36, color=ORANGE, label="Details contain BIC country")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontweight="bold")
    ax2.set_ylim(0, 118)
    ax2.set_ylabel("Percent of payments (%)")
    ax2.legend(frameon=False, fontsize=7.2, loc="upper right")
    ax2.set_title("B. Regional IBAN adoption (Europe 92%–96% vs US/APAC 0%)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")

    ref(fig, 0.62, "Supporting charts: dashboards.pdf, Page 9.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 11: FEATURE GROUP 10 — ANOMALY LABELS
# ==============================================================================
def s11_group10(pdf):
    fig = new("Feature group 10  ·  Anomaly labels", 11)
    fig.text(0.035, 0.905, "Five generative anomaly rules, a shared 1,068-mule pool, and a grounded negative proof",
             fontsize=16.0, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.85,
        "1. Shared 1,068-Mule Syndicate Pool (Romance, CEO & Account Replacement): Decoding our 6-digit PARTY_ID cipher proves all 3 fraud classes route into ONE shared pool of 1,068 mule beneficiary IDs (378 Romance, 634 CEO, 462 Acc.Rep; overlaps |R∩C|=136, |C∩A|=225, |R∩A|=99) in slow offshore banks (mean duration 1,159s–1,558s vs 563s normal; 0.0% last-hop truncation!).\n"
        "   • ROMANCE_SCAM (2,476): 100% C sender; 500 victims each send N ~ U[2..8] escalating wires (med USD 109) with identical details & path.\n"
        "   • CEO_SCAM (945): 100% B sender (72.3% B->C) where B->C amounts are hijacked to the B->B corporate scale (med USD 20,602 vs USD 3,119 normal B->C!).\n"
        "   • ACCOUNT_REPLACEMENT_SCAM (649): Normal party/amount wire whose BENEFICIARY_ACCOUNT is swapped to a mule PARTY_ID in the 1,068 pool.\n"
        "2. Operational Errors & Grounded Negative Result: FAT_FINGER (1,940) shifts decimal by ×10^k (med 71x sender norm, sigma=2.25); DUPLICATE (679) clones 185 wires U[2..5]x (med gap 410s); undocumented CUSTOMER_RECALL (317) is a pure uniform random label (all KS p in [0.22, 0.87]).")
    y = economy(fig, y,
        "Organized laundering syndicates reuse the same offshore money-mule accounts across romance grooming, BEC/CEO executive spoofing, and vendor invoice redirection. "
        "Meanwhile, CUSTOMER_RECALL (SWIFT camt.056) reflects a sender's post-initiation cancellation request (e.g., commercial dispute), so the original MT103 wire is statistically identical to normal traffic.")
    method_block(fig, y,
        "Decoded 6-digit BEN_PID across all 7,006 anomalies to prove the 1,068-mule intersection, conditioned CEO_SCAM on B->C pairs to expose the 7x scale hijack, and ran formal Two-Sample KS tests on CUSTOMER_RECALL vs normal traffic.")

    ad = pd.read_csv("agg/d10_anom_densities.csv")
    ax1 = ax_of(fig, [0.62, 0.54, 0.34, 0.30])
    xb = ad["log10_usd"]
    ax1.plot(xb, ad["NORMAL_BC"], "k--", lw=1.6, label="Normal B->C (USD 3.1k)")
    ax1.plot(xb, ad["ROMANCE_SCAM"], color=PURPLE, lw=1.8, label="Romance (100% C, USD 109)")
    ax1.plot(xb, ad["CEO_SCAM"], color=RED, lw=2.0, label="CEO (72% B->C hijacked to USD 20.6k)")
    ax1.plot(xb, ad["FAT_FINGER_MISTAKE"], color=ORANGE, lw=2.0, label="Fat Finger (×10^k, σ=2.25)")
    ax1.set_xlabel("log10(USD_AMOUNT)")
    ax1.set_ylabel("Density")
    ax1.legend(frameon=False, fontsize=6.8, loc="upper right")
    ax1.set_title("A. Anomaly amount regimes (CEO hijacks B->C scale)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")

    ks = pd.read_csv("agg/d10_ks_recall.csv").iloc[::-1]
    ax2 = ax_of(fig, [0.62, 0.14, 0.34, 0.30])
    short_f = ["len(BEN)", "len(ORD)", "FX_CONV", "PART_CNT", "EPOCH_SEC", "DURATION", "log10(USD)"]
    ax2.barh(short_f, ks["p_val"], color=TEAL, height=0.60)
    ax2.axvline(0.05, color=RED, linestyle="--", lw=1.8, label="α = 0.05 threshold")
    ax2.set_xlim(0, 1.08)
    ax2.set_xlabel("Two-Sample KS p-value vs Normal (all p > 0.22)")
    ax2.legend(frameon=False, fontsize=7.2, loc="lower right")
    ax2.set_title("B. Negative result: CUSTOMER_RECALL (n=317)", loc="left", fontsize=9.6, color=NAVY, fontweight="bold")
    for i, pv in enumerate(ks["p_val"]):
        ax2.text(pv + 0.02, i, f"p={pv:.2f}", va="center", fontsize=7.5, fontweight="bold")

    ref(fig, 0.62, "Supporting charts: dashboards.pdf, Page 10.")
    save(pdf, fig)


# ==============================================================================
# SLIDE 12: MASTER CAUSAL GRAPH, SCREENING BLUEPRINT & ANALYTICAL METHODOLOGY
# ==============================================================================
def s12_synthesis(pdf):
    fig = new("Master Causal Synthesis  ·  Methodology & Screening Blueprint", 12)
    fig.text(0.035, 0.905, "End-to-end structural causal architecture and live-system screening rules",
             fontsize=16.5, color=NAVY, fontweight="bold", va="top")

    # Left half: Visual 7-Stage Causal DAG
    ax = fig.add_axes([0.035, 0.07, 0.48, 0.80], facecolor="#f8fafc")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#cbd5e1"); s.set_linewidth(1.0)
    ax.text(0.50, 0.965, "RECONSTRUCTED 7-STAGE GENERATIVE CAUSAL GRAPH (SCM)", ha="center", va="top", fontsize=9.6, fontweight="bold", color=NAVY)

    dag_boxes = [
        (0.04, 0.77, 0.43, 0.15, "#dbeafe", NAVY, "1. EXOGENOUS WORLD GRAPH\n• Country Zipf Weights, GDP/cap, TZ\n• 8,392 BIC8s ('BBBBCCLO' 0..N-1)\n• Directed Edge Latencies L(B_i→B_j)"),
        (0.53, 0.77, 0.43, 0.15, "#dbeafe", NAVY, "2. PARTY REGISTRY (FAKER)\n• Permanent 6-Digit PARTY_ID Cipher\n• Indep. P(Ord=B)=78.8%, P(Ben=B)=28.8%\n• 100% Home Ord vs 99% Global Ben"),
        (0.04, 0.55, 0.43, 0.16, "#dcfce7", TEAL, "3. TEMPORAL & FX CLOCK\n• Universal 24h Local Curve + TZ Shift\n• 88.8% Weekday + Days 19–30 Surge\n• 92-Day Latent FX(currency, date)"),
        (0.53, 0.55, 0.43, 0.16, "#dcfce7", TEAL, "4. ROUTING & LATENCY ENGINE\n• Hops K ~ ShiftedGeom(1/e = 0.3679)\n• 5%/Hop Dropout ('...' & Boundary)\n• Exact FX Count; D = Σ L_e - 17(K-2)"),
        (0.04, 0.32, 0.43, 0.17, "#f3e8ff", PURPLE, "5. AMOUNT & CURRENCY ENGINE\n• μ_ln = 6 + 2·I(Ord=B) + 2·I(Ben=B)\n• + Sender Country GDP/Capita Scaling\n• 38.7% Round Local × FX(c, date)\n• Path Currency (20:1 B_0 Weight)"),
        (0.53, 0.32, 0.43, 0.17, "#fef3c7", ORANGE, "6. MT103 TEXT & TOKENIZER\n• 83.3% 50K (<line_break:35> wrap)\n• 15.0% 50F ('1/2/3/'), 1.4% 50A\n• 100% B vs C Token Exclusivity\n• 9.3% '//' Prefix; 5.9% No Account"),
        (0.06, 0.04, 0.88, 0.21, "#fee2e2", RED, "7. POST-GENERATION ANOMALY INTERVENTIONS (7,006 ROWS / 0.0701%)\n• Shared 1,068-Mule Pool (Slow Banks, 0% Last Drop): Romance (500×U[2..8] bursts),\n  CEO Scam (100% B; B→C hijacked to B→B scale), Account Replacement (redirected to mule ID)\n• Operational: Fat Finger (×10^k shift, σ=2.25), Duplicate (185 clusters × U[2..5], med 410s)\n• Grounded Negative Result: CUSTOMER_RECALL (317 rows) = Uniform Random Label (KS p > 0.22)")
    ]
    for (bx, by, bw, bh, bg, ec, txt) in dag_boxes:
        p_box = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.012", facecolor=bg, edgecolor=ec, lw=1.3)
        ax.add_patch(p_box)
        ax.text(bx + 0.018, by + bh - 0.018, txt, va="top", ha="left", fontsize=7.5, color=INK, linespacing=1.30)

    for p1, p2 in [
        ((0.25, 0.77), (0.25, 0.71)), ((0.74, 0.77), (0.74, 0.71)),
        ((0.47, 0.84), (0.53, 0.84)), ((0.25, 0.55), (0.25, 0.49)),
        ((0.74, 0.55), (0.74, 0.49)), ((0.47, 0.63), (0.53, 0.63)),
        ((0.25, 0.32), (0.35, 0.25)), ((0.74, 0.32), (0.65, 0.25))
    ]:
        ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5))

    # Right half: Operational Screening Rules & Methodological Summary
    items = [
        ("1. Entity Resolution via 6-Digit PARTY_ID Cipher (CEO & Acct. Replacement)",
         "Screening raw BENEFICIARY_ACCOUNT misses multi-bank syndicates. Extracting PARTY_ID = digits(account)[-6:] links 2.59M accounts and exposes the 1,068 shared mule entities across Romance, CEO, and Account Replacement scams."),
        ("2. Context-Conditional Amount Screening (Fat Finger & CEO B->C Hijacking)",
         "Flag payments >10x–50x the sender's historical median (catching Fat Finger ×10^k shifts) and B->C payments at B->B scale (~USD 20.6k vs USD 3.1k norm, catching CEO Scam)."),
        ("3. Short-Window Deduping & Burst Tracking (Duplicate & Romance Scams)",
         "Flag identical (Ord_Acc, Ben_Acc, Amount, Currency) instructions within 20 minutes (med 410s for the 185 Duplicate clusters vs 15 days for normal repeats) and rapid Consumer bursts (N in 2..8) to offshore accounts."),
        ("4. Value of Grounded Negative Results (CUSTOMER_RECALL & Flat UTC Clock)",
         "Formal KS tests (p in 0.22–0.87) prove CUSTOMER_RECALL (317 rows) has zero feature distortion at initiation, and hourly anomaly rates are flat (0.056%–0.089%). Knowing what NOT to weight prevents false positives."),
        ("5. Full-Population Verification Discipline",
         "Every count, percentage, median, and identity across Dashboards 1–10 and Slides 2–12 is verified on all 10,000,000 rows alongside explicit causal conditioning.")
    ]
    y_r = 0.86
    for title, body in items:
        fig.text(0.54, y_r, title, fontsize=9.1, color=NAVY, fontweight="bold", va="top")
        y_r = para(fig, 0.54, y_r - 0.024, body, 62, size=8.8, color=INK, lead=1.32)
        y_r -= 0.010

    save(pdf, fig)


def main():
    with PdfPages(OUT) as pdf:
        for fn in (
            s01_cover, s02_group1, s03_group2, s04_group3, s05_group4, s06_group5,
            s07_group6, s08_group7, s09_group8, s10_group9, s11_group10, s12_synthesis
        ):
            fn(pdf)
        pdf.infodict()["Title"] = "UMDAC Datathon 2026 — Swift Payments Insights (Team: Plot Twists)"
    print("Wrote ->", OUT)


if __name__ == "__main__":
    main()
