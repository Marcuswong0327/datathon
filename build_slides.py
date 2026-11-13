"""
UMDAC Datathon 2026 — principal insights, one slide per feature group.
Output: insights.pdf
"""
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

OUT = "insights.pdf"
NAVY, ORANGE, TEAL, RED, PURPLE, GREY = (
    "#1f4e79", "#e07b39", "#2a9d8f", "#c0392b", "#8e6bbf", "#7f8c8d")
INK, MUTED, PALE = "#1c2833", "#5d6d7e", "#eef3f8"
W, H = 13.333, 7.5
NS = 14

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#b0b8c1",
})


def chrome(fig, section, page):
    fig.add_artist(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color="white", zorder=-2))
    fig.add_artist(plt.Rectangle((0, 0.955), 1, 0.045, transform=fig.transFigure, color=NAVY, lw=0, zorder=2))
    fig.text(0.035, 0.977, section, color="white", fontsize=9, va="center")
    fig.text(0.965, 0.977, "Swift fictitious payments  ·  UMDAC 2026", color="white",
             fontsize=9, va="center", ha="right")
    fig.text(0.035, 0.028, "Full population, n = 10,000,000.  30 Apr 2023 – 31 Jul 2023, UTC.",
             fontsize=8, color=MUTED, va="center")
    fig.text(0.965, 0.028, f"{page}  /  {NS}", fontsize=8, color=MUTED, va="center", ha="right")


def wrap(text, width):
    return textwrap.wrap(text, width)


def para(fig, x, y, text, width, size=11.5, color=INK, weight="regular", lead=1.38):
    lines = wrap(text, width)
    fig.text(x, y, "\n".join(lines), fontsize=size, color=color, fontweight=weight,
             va="top", linespacing=lead, zorder=3)
    return y - len(lines) * (size * lead) / (H * 72) - 0.012


def new(section, page):
    fig = plt.figure(figsize=(W, H))
    chrome(fig, section, page)
    return fig


def save(pdf, fig):
    pdf.savefig(fig)
    plt.close(fig)


def ax_of(fig, rect):
    ax = fig.add_axes(rect)
    ax.tick_params(labelsize=8, colors=INK, length=3)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)
    return ax


def rule_block(fig, y, text, width=62):
    lines = wrap(text, width)
    line_h = (11.5 * 1.38) / (H * 72)
    h = len(lines) * line_h + 0.055
    fig.add_artist(plt.Rectangle((0.035, y - h), 0.50, h, transform=fig.transFigure,
                                 facecolor=PALE, edgecolor=NAVY, linewidth=0.8, zorder=1))
    fig.text(0.05, y - 0.02, "RECONSTRUCTED RULE", fontsize=8, color=NAVY,
             fontweight="bold", va="top", zorder=3)
    fig.text(0.05, y - 0.048, "\n".join(lines), fontsize=11.5, color=INK, va="top",
             linespacing=1.38, zorder=3)
    return y - h - 0.02


def economy(fig, y, text):
    fig.text(0.035, y, "IF THIS WERE A LIVE PAYMENT SYSTEM", fontsize=8, color=TEAL,
             fontweight="bold", va="top")
    return para(fig, 0.035, y - 0.028, text, 58, size=11, color=INK)


def ref(fig, x, text):
    fig.text(x, 0.072, text, fontsize=8, color=MUTED, va="center")


# ---------------------------------------------------------------- slides
def s01(pdf):
    fig = new("Introduction", 1)
    fig.text(0.035, 0.88, "Reconstructed rules in a synthetic\nSwift payment book",
             fontsize=28, color=NAVY, fontweight="bold", va="top", linespacing=1.15)
    para(fig, 0.035, 0.68,
         "Ten million fictitious payments, 30 April to 31 July 2023. "
         "This deck states the business rules the file actually follows, "
         "one feature group per slide, with the chart that shows the rule "
         "and the live-market behaviour that pattern would represent.",
         90, size=13)
    groups = [
        "1   Data quality and scale",
        "2   Time patterns",
        "3   Currency",
        "4   Payment value",
        "5   Routing and corridors",
        "6   Path structure",
        "7   Duration",
        "8   Party types",
        "9   Accounts and tokens",
        "10  Anomaly labels",
    ]
    fig.text(0.035, 0.48, "ONE SLIDE EACH", fontsize=8, color=NAVY, fontweight="bold")
    for i, g in enumerate(groups):
        col, row = divmod(i, 5)
        fig.text(0.035 + col * 0.42, 0.44 - row * 0.055, g, fontsize=13, color=INK, va="top")
    save(pdf, fig)


def s02(pdf):
    fig = new("Methodology", 2)
    fig.text(0.035, 0.89, "How a pattern became a rule", fontsize=24,
             color=NAVY, fontweight="bold", va="top")
    steps = [
        ("1  Ingest out of core",
         "DuckDB scans the 4.6 GB CSV. The raw file is never loaded into pandas. Columns arrive as text, then amounts, counts, and the timestamp are cast."),
        ("2  Keep a real payment row",
         "A row stays when EPOCH_SECONDS parses as a number. Hour, weekday, and day are extracted in UTC. Domestic means the ordering and beneficiary BIC share a country. Path length counts BIC steps. A path gap is the token ‘…’."),
        ("3  Aggregate the full population",
         "Each feature group is a SQL aggregation. Rates and medians use all 10 million rows. Histogram shapes use a sample drawn after the filter that defines the group. Those samples are not used for the sizes stated here."),
        ("4  Accept only a measured effect",
         "A rule states a condition, an effect, a size, and a scope. It is kept when the chart shows that size on the full file. Where a starting idea disagreed with the chart, the slide states the measured pattern."),
    ]
    y = 0.80
    for title, body in steps:
        fig.text(0.05, y, title, fontsize=13, color=NAVY, fontweight="bold", va="top")
        y = para(fig, 0.05, y - 0.032, body, 105, size=12)
        y -= 0.012
    save(pdf, fig)


def s03(pdf):
    fig = new("Feature group 1  ·  Data quality and scale", 3)
    fig.text(0.035, 0.90, "The book is complete, and labels are rare",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "On every retained row, timestamp, USD amount, BIC path, and both detail fields are populated, and the USD amount is positive. "
        "Exact-duplicate rows are 1 in 10 million. An anomaly label is present on 7,006 payments, which is 0.070 percent. "
        "Scope: the full retained file, 30 April 2023 11:22 UTC through 31 July 2023 09:56 UTC.")
    economy(fig, y,
        "A monitoring team can treat the file as the population, not a sample with a junk tail. "
        "Any screen has to work at about one labelled payment in 1,400. The warning text lives in a column of the first payment. It is not a second pile of broken rows.")
    a = pd.read_csv("agg/d1_anom.csv")
    names = {"NONE": "Unlabelled", "ROMANCE_SCAM": "Romance", "FAT_FINGER_MISTAKE": "Fat finger",
             "CEO_SCAM": "CEO", "DUPLICATE_PAYMENT": "Duplicate",
             "ACCOUNT_REPLACEMENT_SCAM": "Account replacement", "CUSTOMER_RECALL": "Customer recall"}
    a["label"] = a["a"].map(names).fillna(a["a"])
    ax = ax_of(fig, [0.62, 0.22, 0.34, 0.58])
    ax.barh(a["label"][::-1], a["n"].to_numpy()[::-1], color=ORANGE, height=0.72)
    ax.set_xscale("log")
    ax.set_xlabel("Payments (log scale)")
    ax.set_title("Label counts on the full file", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.62, "Same counts: dashboard page 1, upper right.")
    save(pdf, fig)


def s04(pdf):
    fig = new("Feature group 2  ·  Time patterns", 4)
    fig.text(0.035, 0.90, "The book moves west through the UTC day",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "The UTC hour with the most payments shifts with the sender’s country: China 08:00, Japan 09:00, Singapore 10:00, Germany 15:00, France and Switzerland 17:00, Britain 18:00, the United States 23:00. "
        "A weekday carries 1.70–1.83 million payments. Saturday carries 0.43 million and Sunday 0.68 million. "
        "The label rate stays between 0.056 percent and 0.089 percent in every UTC hour. Scope: all payments.")
    economy(fig, y,
        "People pay during their own working day, so Asian banks fill the UTC morning, European banks the UTC afternoon, and US banks the late UTC evening. "
        "The weekend book is about one third of a weekday. An after-hours screen sees the same label rate as midday.")
    hc = pd.read_csv("agg/d2_hour_by_country.csv")
    ax = ax_of(fig, [0.56, 0.30, 0.40, 0.50])
    colors = {"US": NAVY, "GB": ORANGE, "DE": TEAL, "FR": RED, "CH": PURPLE, "SG": GREY}
    for oc, g in hc.groupby("oc"):
        g = g.sort_values("hr")
        ax.plot(g["hr"], 100 * g["n"] / g["n"].sum(), color=colors.get(oc, INK), lw=1.8, label=oc)
    ax.set_xlim(0, 23)
    ax.set_xlabel("Hour, UTC")
    ax.set_ylabel("Share of that country’s payments (%)")
    ax.legend(ncol=6, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    ax.set_title("Six largest senders", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.56, "Weekday bars and the hourly label rate: dashboard page 2.")
    save(pdf, fig)


def s05(pdf):
    fig = new("Feature group 3  ·  Currency", 5)
    fig.text(0.035, 0.90, "The sender’s country picks the currency",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "For each of the 12 largest sending countries, 86–95 percent of payments use that country’s home currency: the euro in France, Germany, Italy, Belgium, Luxembourg, and the Netherlands; the dollar for 90.5 percent of US senders; the franc 88.8 percent; sterling 88.6 percent; the Singapore dollar 87.5 percent; the yuan 86.2 percent; the Hong Kong dollar 88.3 percent. "
        "A cross-border payment is converted 93 percent of the time. A domestic payment is converted 37 percent of the time. Scope: all payments.")
    economy(fig, y,
        "Firms and people pay in the currency of the bank that sends, which is how a local clearing currency becomes the default. "
        "Crossing a border usually means an FX ticket. Staying inside one country still converts more than a third of the time, so a domestic flag is a weak substitute for an FX flag.")
    rows = [("US", "USD", 90.5), ("CH", "CHF", 88.8), ("GB", "GBP", 88.6), ("FR", "EUR", 94.0),
            ("DE", "EUR", 94.5), ("SG", "SGD", 87.5), ("CN", "CNY", 86.2), ("IT", "EUR", 93.3)]
    ax = ax_of(fig, [0.60, 0.22, 0.36, 0.58])
    labels = [f"{a}  {b}" for a, b, _ in rows][::-1]
    vals = [v for _, _, v in rows][::-1]
    ax.barh(labels, vals, color=NAVY, height=0.72)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of that country’s payments (%)")
    ax.set_title("Home currency, eight largest senders", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.60, "Domestic versus cross-border FX: dashboard page 3, lower right.")
    save(pdf, fig)


def s06(pdf):
    fig = new("Feature group 4  ·  Payment value", 6)
    fig.text(0.035, 0.90, "Amounts sit on a log scale, and round numbers stick",
             fontsize=18, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "log10 of the USD amount is a single hump, the shape of a log-normal book. "
        "Among whole-dollar amounts from 100 to 100,000, the most common values are 10,000 (35,650 payments), 1,000 (32,630), 5,000 (21,709), and 100,000 (16,995). "
        "The level of the amount follows who is paying: both parties business, median 22,888 dollars; either side a consumer, about 3,200 dollars; both consumers, 463 dollars. Scope: all payments; the shape is the full-file histogram on dashboard page 4.")
    economy(fig, y,
        "Payment size multiplies rather than adds: a typical firm payment and a typical household payment live an order of magnitude apart. "
        "Round amounts are price points and invoice conventions, the same way a cash economy piles up on notes of 100 and 1,000.")
    r = pd.read_csv("agg/d4_round.csv").head(6)
    ax = ax_of(fig, [0.60, 0.24, 0.36, 0.54])
    labels = [f"{int(v):,}" for v in r["f"]][::-1]
    ax.barh(labels, r["n"].to_numpy()[::-1], color=ORANGE, height=0.7)
    ax.set_xlabel("Payments at this whole-dollar amount")
    ax.set_title("Most common round amounts", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.60, "Log-amount shape and party-type histograms: dashboard page 4.")
    save(pdf, fig)


def s07(pdf):
    fig = new("Feature group 5  ·  Routing and corridors", 7)
    fig.text(0.035, 0.90, "Traffic hubs through the United States",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "The file contains 26,764 corridors. The largest, United States to United States, is 385,598 payments, 3.9 percent of the book. The top 15 corridors are 16.1 percent. "
        "The most repeated bank pair, 0001MQM0 to 0009TNT0, occurs 20,005 times. "
        "Sender and beneficiary banks share a country on 24 percent of US payments and on under 10 percent for every other large sender. Scope: all payments.")
    economy(fig, y,
        "This is a correspondent network with a dollar hub, plus a large domestic American book. "
        "Bank pairs do repeat, which is what a sticky relationship looks like, and the long tail of 26,764 corridors is what an open network looks like. No single pair is the market.")
    cor = pd.read_csv("agg/d5_corridors.csv")
    cor["k"] = cor["oc"] + " → " + cor["bc"]
    top = cor.nlargest(8, "n").iloc[::-1]
    ax = ax_of(fig, [0.58, 0.22, 0.38, 0.56])
    ax.barh(top["k"], top["n"].to_numpy(), color=ORANGE, height=0.7)
    ax.set_xlabel("Payments")
    ax.set_title("Eight largest corridors", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.58, "Heatmap, BIC pairs, and domestic share: dashboard page 5.")
    save(pdf, fig)


def s08(pdf):
    fig = new("Feature group 6  ·  Path structure", 8)
    fig.text(0.035, 0.90, "The product sets the path, and the path sets the FX",
             fontsize=18, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "Direct is exactly two participants: 6,323,280 payments, every Direct payment, and no Covered or Indirect payment has two. "
        "Path length equals the participant count on 92.3 percent of payments, and equals that count plus the gap token on 99.4 percent. "
        "CONTINUITY_QFLAG is N exactly when the path contains ‘…’: 767,204 payments, and zero rows disagree. "
        "Mean FX conversions rise by about 0.85 for each bank added, from 0.84 at two banks. Scope: all payments.")
    economy(fig, y,
        "Direct is a two-bank product. Covered and Indirect are the same payment handed along a chain. "
        "Each extra bank is another place a currency can change, so the FX count walks up almost one for one with the chain. A ‘…’ in the path is a missing link in that chain, and the continuity flag is that fact written twice.")
    conv = pd.read_csv("agg/d6_conv.csv")
    conv = conv[conv["part"].between(2, 12)]
    ax = ax_of(fig, [0.58, 0.24, 0.38, 0.54])
    ax.plot(conv["part"], conv["mean_conv"], color=NAVY, marker="o", lw=2)
    ax.set_xlabel("Banks on the payment")
    ax.set_ylabel("Mean FX conversions")
    ax.set_title("One more bank, almost one more conversion", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.58, "Participant mix, path heatmap, continuity table: dashboard page 6.")
    save(pdf, fig)


def s09(pdf):
    fig = new("Feature group 7  ·  Duration", 9)
    fig.text(0.035, 0.90, "Each extra bank adds waiting time",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "Median duration is 39 seconds for Direct, 281 seconds for Indirect, and 383 seconds for Covered. "
        "It rises with the chain: 39 seconds at two banks, 126 at three, 418 at four, 1,704 at ten, and 2,171 at twelve. "
        "A path that contains ‘…’ has median 155 seconds; a continuous path has median 54 seconds. "
        "The cross-border median is 55 seconds and the domestic median is 167 seconds. Scope: all payments. The far tail, past twelve banks, is a few dozen payments.")
    economy(fig, y,
        "Duration here is processing and hand-off time, not the length of a flight. A direct payment clears in under a minute at the median. "
        "A covered or indirect payment waits through extra banks. A gap in the path is a repair. Crossing a border, on its own, is not the slow case in this file.")
    part = pd.read_csv("agg/d7_part.csv")
    part = part[part["part"].between(2, 12)]
    ax = ax_of(fig, [0.58, 0.24, 0.38, 0.54])
    ax.plot(part["part"], part["med"], color=NAVY, marker="o", lw=2, label="Median")
    ax.plot(part["part"], part["p90"], color=ORANGE, marker="o", lw=1.5, label="90th percentile")
    ax.set_xlabel("Banks on the payment")
    ax.set_ylabel("Seconds")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Duration against the length of the chain", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.58, "Duration by product and by path gap: dashboard page 7.")
    save(pdf, fig)


def s10(pdf):
    fig = new("Feature group 8  ·  Party types", 10)
    fig.text(0.035, 0.90, "Households pay hundreds. Firms pay tens of thousands.",
             fontsize=18, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "Business-to-consumer is the modal flow, 5.60 million payments, median 3,119 dollars. "
        "Business-to-business is 2.27 million payments, median 22,888 dollars. "
        "Consumer-to-business is 0.61 million, median 3,229 dollars. Consumer-to-consumer is 1.51 million, median 463 dollars. "
        "The sender is a business on 75–86 percent of payments in every large country, and that share is about four fifths for Direct, Covered, and Indirect alike. Scope: all payments.")
    economy(fig, y,
        "Consumers move household money. Firms move invoices and treasury. "
        "The routing product does not pick the customer, and the sender’s country does not either: every large market in this file is a business-heavy book inside a narrow band.")
    m = pd.read_csv("agg/d8_types.csv")
    m["k"] = m["oty"] + " → " + m["bty"]
    order = ["B → B", "B → C", "C → B", "C → C"]
    m = m.set_index("k").loc[order]
    ax = ax_of(fig, [0.58, 0.24, 0.38, 0.54])
    bars = ax.bar(order, m["med"], color=[NAVY, ORANGE, TEAL, RED], width=0.72)
    ax.set_ylabel("Median USD")
    ax.set_title("Median amount by who pays whom", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    for b, v in zip(bars, m["med"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 400, f"{v:,.0f}", ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_ylim(0, 28000)
    ref(fig, 0.58, "Counts, country mix, and routing mix: dashboard page 8.")
    save(pdf, fig)


def s11(pdf):
    fig = new("Feature group 9  ·  Accounts and tokens", 11)
    fig.text(0.035, 0.90, "Europe carries an IBAN. The active accounts are few.",
             fontsize=18, color=NAVY, fontweight="bold", va="top")
    y = rule_block(fig, 0.84,
        "There are 391,132 ordering accounts. A third are used once, the median account sends 3 payments, and the busiest sends 75,803. The top 1 percent of ordering accounts send 46 percent of payments. "
        "Of 2.59 million beneficiary accounts, 78 percent receive a single payment. "
        "An IBAN token is on 91–96 percent of payments from Switzerland, Britain, and the euro area, and on 0 percent from the US, Singapore, China, Hong Kong, Japan, Australia, and the Isle of Man. "
        "Ordering details contain the BIC country code on 97–100 percent of European payments and on 67–78 percent from the US, Singapore, China, and Hong Kong. Scope: all payments.")
    economy(fig, y,
        "European rails in this file identify the account with an IBAN. US and Asian rails do not. "
        "Origination is a wholesale pattern: many quiet accounts, and a small set that sends nearly half the book. Beneficiary accounts look like invoices, opened for one payment.")
    labels = ["US", "CH", "GB", "FR", "DE", "SG", "CN", "HK"]
    iban = [0, 92.4, 92.0, 92.1, 92.1, 0, 0, 0]
    detail = [72.6, 98.8, 97.7, 99.6, 98.7, 66.7, 68.2, 77.6]
    ax = ax_of(fig, [0.58, 0.26, 0.38, 0.50])
    import numpy as np
    x = np.arange(len(labels))
    ax.bar(x - 0.18, iban, width=0.36, color=NAVY, label="IBAN token")
    ax.bar(x + 0.18, detail, width=0.36, color=TEAL, label="Details name the country")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 128)
    ax.set_ylabel("Percent of payments")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("What the sender’s text reveals", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.58, "Payments-per-account histograms: dashboard page 9.")
    save(pdf, fig)


def s12(pdf):
    fig = new("Feature group 10  ·  Anomaly labels", 12)
    fig.text(0.035, 0.90, "Four labels have a signature. Two do not.",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    rows = [
        ("Romance", "2,476", "Always a consumer sender. 73% pay a consumer. Median $109. Median of 6 payments to the same beneficiary. 97% cross-border."),
        ("Fat finger", "1,940", "Median is 71× what that ordering account usually sends. 64% are at least 10×. 53% are at least 50×. A narrow band around exactly 10× holds 3.5%, and around 100× holds 4.3%."),
        ("CEO", "945", "Always a business sender. 99% cross-border. Median $20,602, beside the ordinary business-to-business median of $22,883."),
        ("Duplicate", "679", "The same two accounts, amount, and currency return after a median of 18 minutes. Other repeats of that key return after 15 days."),
        ("Account replacement", "649", "99.4% cross-border. A first-seen beneficiary account is 18% of these payments and 21% of ordinary payments."),
        ("Customer recall", "317", "Median $3,164 and 78% business senders, in line with the ordinary book. No separate signature in amount, party, or corridor."),
    ]
    y = 0.82
    for name, n, text in rows:
        fig.text(0.035, y, name, fontsize=10, color=NAVY, fontweight="bold", va="top")
        fig.text(0.20, y, n, fontsize=10, color=ORANGE, fontweight="bold", va="top")
        y = para(fig, 0.28, y, text, 48, size=9, color=INK, lead=1.25)
        y -= 0.004
    ax = ax_of(fig, [0.60, 0.42, 0.35, 0.38])
    labs = ["At least\n10×", "At least\n50×", "Near\nexactly 10×", "Near\nexactly 100×"]
    vals = [63.9, 53.0, 3.5, 4.3]
    ax.bar(labs, vals, color=[NAVY, NAVY, GREY, GREY], width=0.72)
    ax.set_ylim(0, 90)
    ax.set_ylabel("Share of fat-finger payments (%)")
    ax.set_title("Against the sender’s own median", loc="left", fontsize=11, color=NAVY, fontweight="bold")
    ref(fig, 0.60, "Duplicate-gap histogram: dashboard page 10.")
    para(fig, 0.035, 0.145,
         "In a live system this is an extra keystroke on a familiar account, a double submit in one sitting, and a repeated small personal transfer abroad.",
         115, size=11)
    save(pdf, fig)


def s13(pdf):
    fig = new("Using the rules", 13)
    fig.text(0.035, 0.89, "What an investigator would actually screen on",
             fontsize=20, color=NAVY, fontweight="bold", va="top")
    items = [
        ("Amount versus the sender’s own history",
         "Flag a payment near 50 times that ordering account’s median, and wider. A fixed dollar cutoff misses a 71× fat finger on a small account and catches ordinary business payments."),
        ("A short duplicate window",
         "Same ordering account, beneficiary account, amount, and currency inside about 20 minutes. A window of days mixes the labelled duplicates with ordinary repeats."),
        ("Romance as a repeated personal flow",
         "A consumer sender, a small amount, a cross-border beneficiary who already received several of these payments."),
        ("Leave the clock out of the fraud score",
         "The label rate is flat across the UTC day. Hour of day describes where the sender sits, which is useful for operations and useless as a suspicion score in this file."),
        ("Read FX off the conversion count",
         "Domestic payments still convert 37 percent of the time. The conversion count, and the length of the bank chain, are the FX rules."),
        ("Treat path and duration as operations",
         "Participant count, the ‘…’ token, and duration move together. Labelled payments sit near 2.5 banks, the same neighbourhood as ordinary Direct traffic, so the chain is a service clock rather than a fraud feature."),
    ]
    y = 0.78
    for title, body in items:
        fig.text(0.05, y, title, fontsize=12.5, color=NAVY, fontweight="bold", va="top")
        y = para(fig, 0.05, y - 0.028, body, 108, size=11.5)
        y -= 0.008
    save(pdf, fig)


def s14(pdf):
    fig = new("Limits", 14)
    fig.text(0.035, 0.89, "What these rules are, and what they are not",
             fontsize=22, color=NAVY, fontweight="bold", va="top")
    items = [
        ("The file is synthetic.",
         "Swift states that the payments were generated from hard-coded rules, NumPy draws, and the Faker library. The rules above describe this file. The economic readings are what the same pattern would mean in a live system."),
        ("Small labels stay thin.",
         "Customer recall has 317 payments and account replacement has 649. A signature that is absent at that size may be absent because the generator did not write one, or because these fields cannot see it."),
        ("Two familiar stories are not in the columns we tested.",
         "A CEO payment is not larger than an ordinary business-to-business payment. A first-seen beneficiary account is about as common on account-replacement payments as on ordinary ones. A ‘new beneficiary’ test beyond that pair was not run."),
        ("Samples never carry a size.",
         "Every percentage, median, and count in this deck is a full-population aggregate. Samples were used only to draw distribution shapes on the dashboard."),
    ]
    y = 0.78
    for title, body in items:
        fig.text(0.05, y, title, fontsize=14, color=NAVY, fontweight="bold", va="top")
        y = para(fig, 0.05, y - 0.034, body, 100, size=13)
        y -= 0.02
    save(pdf, fig)


def main():
    with PdfPages(OUT) as pdf:
        for fn in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14):
            fn(pdf)
        pdf.infodict()["Title"] = "UMDAC 2026 — reconstructed rules in Swift fictitious payments"
    print("wrote", OUT)


if __name__ == "__main__":
    main()
