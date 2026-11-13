"""
UMDAC Datathon 2026 - Swift payments: end-to-end dashboard builder
------------------------------------------------------------------
Usage:
    pip install duckdb pandas matplotlib numpy
    python build_dashboard.py path/to/your_4GB_file.csv

What it does
  1. Loads the 4 GB CSV out-of-core with DuckDB (never loads it all into RAM)
  2. Cleans it (drops the DISCLAIMER/WARNING row, casts types, derives features)
  3. Runs aggregate SQL per feature group (only small result tables reach pandas)
  4. Draws one dashboard page per feature group -> dashboards.pdf  (10 pages)
  5. Writes every aggregate to ./agg/*.csv so you can quote numbers in the slides

Dashboard text boxes: edit the RULES dict AFTER you have looked at the charts.
The defaults are HYPOTHESES to test, not findings.
"""
import sys, os, textwrap
import duckdb, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

SRC = sys.argv[1] if len(sys.argv) > 1 else "swift_umdac_datathon_2026_fictitious_payment_data.csv"
SRC = os.path.abspath(SRC).replace("\\", "/")
DB, OUT, AGG = "swift.duckdb", "dashboards.pdf", "agg"
os.makedirs(AGG, exist_ok=True)
os.makedirs("tmp_duckdb", exist_ok=True)
con = duckdb.connect(DB)
con.execute("PRAGMA threads=8")
con.execute("SET memory_limit='20GB'")
con.execute("SET preserve_insertion_order=false")
con.execute("SET temp_directory='tmp_duckdb'")
con.execute("SET TimeZone='UTC'")

# ------------------------------------------------------------------ 1. LOAD
if not con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='t'").fetchone()[0]:
    print("loading csv into duckdb...", flush=True)
    con.execute(f"""CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv('{SRC}',
        header=true, all_varchar=true, ignore_errors=true, sample_size=100000,
        quote='"', escape='"', strict_mode=false, encoding='utf-8')""")
    cols = [c[0] for c in con.execute("DESCRIBE raw").fetchall()]
    print("columns:", cols)

    def col(prefix):  # robust to CURRENCY vs CURRENCY_CODE etc.
        m = [c for c in cols if c.upper().startswith(prefix)]
        if not m: raise SystemExit(f"column starting with {prefix} not found in {cols}")
        return f'"{m[0]}"'

    con.execute(f"""
    CREATE OR REPLACE TABLE t AS
    SELECT
      to_timestamp(TRY_CAST({col('EPOCH')} AS DOUBLE))            AS ts,
      {col('CURRENCY_CODE') if any(c.upper()=='CURRENCY_CODE' for c in cols) else col('CURRENCY')} AS cur,
      TRY_CAST({col('USD_AMOUNT')} AS DOUBLE)                      AS usd,
      {col('ORDERING_BIC8')}  AS ob,  {col('BENEFICIARY_BIC8')} AS bb,
      {col('BIC8_PATH')}      AS path,
      TRY_CAST({col('TOTAL_DUR')} AS DOUBLE)                       AS dur,
      {col('CONTINUITY')}     AS cont,
      TRY_CAST({col('CURRENCY_CONV')} AS INT)                      AS conv,
      TRY_CAST({col('PARTICIPANT')} AS INT)                        AS part,
      {col('TRANSACTION_TYPE')} AS typ,
      {col('ORDERING_ACCOUNT')} AS oacc, {col('BENEFICIARY_ACCOUNT')} AS bacc,
      {col('ORDERING_DETAILS')} AS odet, {col('ORDERING_TOKENS')} AS otok,
      {col('BENEFICIARY_DETAILS')} AS bdet, {col('BENEFICIARY_TOKENS')} AS btok,
      {col('ORDERING_TYPE')} AS oty, {col('BENEFICIARY_TYPE')} AS bty,
      NULLIF({col('ANOMALY')}, '') AS anom,
      substr({col('ORDERING_BIC8')},5,2)    AS oc,      -- country of sending bank (BIC chars 5-6)
      substr({col('BENEFICIARY_BIC8')},5,2) AS bc
    FROM raw
    WHERE TRY_CAST({col('EPOCH')} AS DOUBLE) IS NOT NULL      -- drops the DISCLAIMER/WARNING row
    """)
    con.execute("""
    CREATE OR REPLACE TABLE t2 AS SELECT *,
      extract(hour FROM ts) AS hr, extract(dow FROM ts) AS dow, date_trunc('day', ts) AS day,
      (oc = bc) AS domestic,
      length(path) - length(replace(path, ';', '')) + 1 AS path_len,
      (path LIKE '%...%') AS path_gap,
      log10(greatest(usd, 0.01)) AS lusd
    FROM t""")
    con.execute("DROP TABLE t; ALTER TABLE t2 RENAME TO t; DROP TABLE raw")

# Hour, weekday and day were derived with extract()/date_trunc(), which follow the
# session time zone. Rebuild them if a previous run stored local time instead of UTC.
mismatch = con.execute("""
    SELECT count(*) FROM (
        SELECT 1 FROM t WHERE hr IS DISTINCT FROM extract(hour FROM ts) LIMIT 1
    )
""").fetchone()[0]
if mismatch:
    print("aligning hour/day features to UTC...", flush=True)
    con.execute("""
        CREATE OR REPLACE TABLE t_utc AS
        SELECT * REPLACE (
            extract(hour FROM ts) AS hr,
            extract(dow FROM ts) AS dow,
            date_trunc('day', ts) AS day
        ) FROM t
    """)
    con.execute("DROP TABLE t")
    con.execute("ALTER TABLE t_utc RENAME TO t")

def q(sql, name=None):
    df = con.execute(sql).df()
    if name: df.to_csv(f"{AGG}/{name}.csv", index=False)
    return df

N = con.execute("SELECT count(*) FROM t").fetchone()[0]
print("rows:", N)

# ------------------------------------------------------------------ 2. STYLE HELPERS
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9, "axes.titleweight": "bold"})
C = ["#1f4e79", "#e07b39", "#2a9d8f", "#c0392b", "#8e6bbf", "#7f8c8d"]

# EDIT THESE after inspecting the charts. State: condition -> effect -> size -> scope.
RULES = {
 "1. Data quality & scale": "H: DISCLAIMER row + malformed rows are the only junk; no duplicate rows. Record counts, null rates and anomaly prevalence shown as baseline.",
 "2. Time patterns": "H: Volume follows business hours of the SENDER's country (UTC hour shifts by country); weekday >> weekend; anomalies may cluster off-hours.",
 "3. Currency": "H: Currency is driven by the beneficiary/ordering country (EUR for euro-zone BICs); domestic payments rarely FX; a few currencies dominate volume.",
 "4. Payment value": "H: Amounts are log-normal; scale depends on currency, B vs C party type and corridor; Business >> Consumer.",
 "5. Routing & corridors": "H: Corridors (ordering country -> beneficiary country) are concentrated; ordering/beneficiary BIC pairs are sticky.",
 "6. Path structure": "H: TRANSACTION_TYPE determines PARTICIPANT_COUNT (Direct=2); path length = participants; FX count rises with participants & cross-currency corridors.",
 "7. Duration": "H: TOTAL_DURATION grows with participants and across time zones; Covered/Indirect slower than Direct; heavy right tail.",
 "8. Party types": "H: B/C mix depends on amount & corridor; consumer-to-consumer payments are small; B->B large.",
 "9. Party details & accounts": "H: Account reuse follows a power law; tokens (IBAN, country code) depend on country; detail text mirrors BIC country.",
 "10. Anomalies": "H: Each ANOMALY_TYPE has a signature: FAT_FINGER = amount x10/x100 vs sender norm; DUPLICATE = same acct/amount repeated in short window; ROMANCE = repeated C->C to one beneficiary; CEO = B, large, new beneficiary; ACCOUNT_REPLACEMENT = known beneficiary BIC, new account.",
}

def page(pdf, title, draw, n=4):
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.suptitle(title, x=0.04, ha="left", fontsize=17, fontweight="bold", color=C[0], y=0.975)
    fig.text(0.04, 0.925, "\n".join(textwrap.wrap("RULE / HYPOTHESIS: " + RULES[title], 190)),
             fontsize=9.5, va="top", bbox=dict(boxstyle="round", fc="#eef3f8", ec=C[0]))
    gs = fig.add_gridspec(2, 2, left=0.14, right=0.97, top=0.84, bottom=0.09, hspace=0.48, wspace=0.30)
    axes = [fig.add_subplot(gs[i // 2, i % 2]) for i in range(n)]
    draw(axes)
    fig.text(0.04, 0.012, f"Source: Swift artificial payments dataset (n={N:,}). All charts computed on the full data.", fontsize=7, color="grey")
    pdf.savefig(fig); plt.close(fig)

def bar(ax, s, title, color=C[0], horiz=False, fmt=None, xlabel=None, ylabel=None):
    n = len(s)
    if horiz:
        s.plot.barh(ax=ax, color=color, width=0.8)
        ax.invert_yaxis()
        ax.tick_params(axis="y", labelsize=6 if n > 8 else 7)
    else:
        longest = max((len(str(i)) for i in s.index), default=0)
        rot = 40 if n > 10 and longest >= 3 else 0
        s.plot.bar(ax=ax, color=color, width=0.8, rot=rot)
        ax.tick_params(axis="x", labelsize=6 if n > 8 else 7)
    ax.set_title(title); ax.set_xlabel(xlabel or ""); ax.set_ylabel(ylabel or "")

# ------------------------------------------------------------------ 3. DASHBOARD PAGES
def d1(ax):
    nulls = q("""SELECT 'ts' c, avg((ts IS NULL)::int) r FROM t UNION ALL SELECT 'usd', avg((usd IS NULL)::int) FROM t
        UNION ALL SELECT 'path', avg((path IS NULL)::int) FROM t UNION ALL SELECT 'odet', avg((odet IS NULL)::int) FROM t
        UNION ALL SELECT 'bdet', avg((bdet IS NULL)::int) FROM t UNION ALL SELECT 'unlabelled', avg((anom IS NULL)::int) FROM t""", "d1_nulls")
    bar(ax[0], nulls.set_index("c").r * 100, "Share of rows with NULL (%) - anomaly NULL = normal traffic", C[3], True)
    a = q("SELECT coalesce(anom,'NONE') a, count(*) n FROM t GROUP BY 1 ORDER BY 2 DESC", "d1_anom")
    bar(ax[1], a.set_index("a").n, "Anomaly label counts (log scale)", C[1], True); ax[1].set_xscale("log")
    d = q("SELECT day, count(*) n FROM t GROUP BY 1 ORDER BY 1", "d1_daily")
    ax[2].plot(d.day, d.n, color=C[0]); ax[2].set_title("Daily payment volume (time coverage)")
    dup = q("SELECT (SELECT count(*) FROM t) total, (SELECT count(*) FROM (SELECT DISTINCT * FROM t)) uniq")
    ax[3].axis("off"); ax[3].text(0, .8, f"Rows: {int(dup.total[0]):,}\nExact-duplicate rows: {int(dup.total[0]-dup.uniq[0]):,}\n"
        f"Date range: {d.day.min():%Y-%m-%d} to {d.day.max():%Y-%m-%d}\nZero/negative USD: {con.execute('SELECT count(*) FROM t WHERE usd<=0').fetchone()[0]:,}", fontsize=12, va="top")
    ax[3].set_title("Integrity checks")

def d2(ax):
    h = q("SELECT hr, count(*) n FROM t GROUP BY 1 ORDER BY 1", "d2_hour")
    bar(ax[0], h.set_index("hr").n, "Payments by UTC hour")
    w = q("SELECT dow, count(*) n FROM t GROUP BY 1 ORDER BY 1", "d2_dow")
    bar(ax[1], w.set_index("dow").n, "Payments by day of week (0=Sun)", C[1])
    top = q("SELECT oc FROM t GROUP BY 1 ORDER BY count(*) DESC LIMIT 6")["oc"].tolist()
    hc = q(f"SELECT oc, hr, count(*)::double n FROM t WHERE oc IN {tuple(top)} GROUP BY 1,2", "d2_hour_by_country")
    for i, (k, g) in enumerate(hc.groupby("oc")):
        g = g.sort_values("hr"); ax[2].plot(g.hr, g.n / g.n.sum(), label=k, color=C[i % 6])
    ax[2].legend(ncol=3); ax[2].set_title("Hour profile by sending country (peak shifts = local business hours?)")
    an = q("SELECT hr, avg((anom IS NOT NULL)::int)*100 r FROM t GROUP BY 1 ORDER BY 1", "d2_anom_hour")
    bar(ax[3], an.set_index("hr").r, "Anomaly rate (%) by UTC hour", C[3])

def d3(ax):
    c = q("SELECT cur, count(*) n, avg(usd) mean_usd, median(usd) med_usd FROM t GROUP BY 1 ORDER BY n DESC LIMIT 15", "d3_currency")
    bar(ax[0], c.set_index("cur").n, "Top-15 currencies by count (log)", horiz=True); ax[0].set_xscale("log")
    m = q("SELECT oc, cur, count(*) n FROM t GROUP BY 1,2", "d3_country_currency")
    top = m.groupby("oc").n.sum().nlargest(10).index
    pv = m[m.oc.isin(top)].pivot_table(index="oc", columns="cur", values="n", fill_value=0)
    pv = pv.loc[:, pv.sum().nlargest(8).index]; pv = pv.div(pv.sum(1), axis=0)
    pv.plot.bar(stacked=True, ax=ax[1], width=.85, rot=0)
    ax[1].set_title("Currency mix by sending country (share)")
    ax[1].legend(ncol=4, fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
    bar(ax[2], c.set_index("cur").med_usd, "Median USD by currency (top-15 by volume)", C[1])
    x = q("SELECT domestic, avg((conv>0)::int)*100 fx FROM t GROUP BY 1", "d3_fx_domestic")
    fx = x.set_index("domestic").fx
    fx.index = fx.index.map(lambda v: "domestic" if v else "cross-border")
    bar(ax[3], fx, "% of payments with at least one FX conversion", C[2])

def d4(ax):
    s = q("SELECT lusd FROM t USING SAMPLE 500000 ROWS")
    ax[0].hist(s.lusd, bins=80, color=C[0]); ax[0].set_title("log10(USD amount): shape (normal => log-normal)")
    b = q("SELECT oty, bty, lusd FROM t USING SAMPLE 500000 ROWS")
    for i, (k, g) in enumerate(b.groupby(["oty", "bty"])): ax[1].hist(g.lusd, bins=60, alpha=.5, density=True, label=f"{k[0]}->{k[1]}", color=C[i % 6])
    ax[1].legend(); ax[1].set_title("Amount by ordering->beneficiary type")
    c = q("SELECT cur, median(usd) med, quantile_cont(usd,.9) p90 FROM t GROUP BY 1 HAVING count(*)>2000 ORDER BY med DESC LIMIT 15", "d4_cur_median")
    c.set_index("cur")[["med", "p90"]].plot.bar(ax=ax[2], color=[C[0], C[1]], logy=True, rot=40)
    ax[2].tick_params(axis="x", labelsize=6)
    ax[2].set_title("Median and P90 USD by currency")
    r = q("SELECT floor(usd) f, count(*) n FROM t WHERE usd BETWEEN 100 AND 100000 AND usd=round(usd,0) GROUP BY 1 HAVING count(*)>0 ORDER BY n DESC LIMIT 15", "d4_round")
    ax[3].axis("off"); ax[3].set_title("Round-number amounts (top values)"); ax[3].text(0, 1, r.to_string(index=False), family="monospace", va="top")

def d5(ax):
    cor = q("SELECT oc, bc, count(*) n FROM t GROUP BY 1,2", "d5_corridors")
    top = cor.groupby("oc").n.sum().nlargest(12).index; topb = cor.groupby("bc").n.sum().nlargest(12).index
    pv = cor[cor.oc.isin(top) & cor.bc.isin(topb)].pivot_table(index="oc", columns="bc", values="n", fill_value=0)
    ax[0].imshow(np.log1p(pv.values), cmap="Blues"); ax[0].set_xticks(range(len(pv.columns))); ax[0].set_xticklabels(pv.columns, rotation=0, fontsize=7)
    ax[0].set_yticks(range(len(pv.index))); ax[0].set_yticklabels(pv.index); ax[0].set_title("Corridor heatmap (log count): sender rows -> beneficiary cols")
    tc = cor.nlargest(15, "n"); tc.index = tc.oc + ">" + tc.bc; bar(ax[1], tc.n, "Top-15 corridors", C[1], True)
    b = q("SELECT ob, bb, count(*) n FROM t GROUP BY 1,2 ORDER BY n DESC LIMIT 15", "d5_bicpairs"); b.index = b.ob + ">" + b.bb
    bar(ax[2], b.n, "Top-15 BIC pairs (sticky relationships?)", C[2], True)
    dom = q("SELECT oc, avg(domestic::int)*100 d FROM t GROUP BY 1 ORDER BY count(*) DESC LIMIT 15", "d5_domestic")
    bar(ax[3], dom.set_index("oc").d, "% of payments where sender and beneficiary bank share a country", C[4])

def d6(ax):
    a = q("SELECT typ, part, count(*) n FROM t GROUP BY 1,2", "d6_type_part")
    a.pivot_table(index="typ", columns="part", values="n", fill_value=0).pipe(lambda p: p.div(p.sum(1), axis=0)).plot.bar(stacked=True, ax=ax[0], rot=0)
    ax[0].set_title("Participant count mix by TRANSACTION_TYPE")
    ax[0].legend(title="part", fontsize=5, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False)
    b = q("SELECT part, path_len, count(*) n FROM t GROUP BY 1,2", "d6_part_pathlen")
    pv = b.pivot_table(index="part", columns="path_len", values="n", fill_value=0)
    ax[1].imshow(np.log1p(pv.values), cmap="Greens", aspect="auto"); ax[1].set_title("PARTICIPANT_COUNT (rows) vs BIC path length (cols), log count")
    ax[1].set_yticks(range(len(pv.index))); ax[1].set_yticklabels(pv.index); ax[1].set_xticks(range(len(pv.columns))); ax[1].set_xticklabels(pv.columns)
    c = q("SELECT part, avg(conv) mean_conv FROM t GROUP BY 1 ORDER BY 1", "d6_conv"); bar(ax[2], c.set_index("part").mean_conv, "Mean FX conversions by participant count", C[1])
    d = q("SELECT cont, path_gap, count(*) n FROM t GROUP BY 1,2", "d6_continuity")
    ax[3].axis("off"); ax[3].set_title("CONTINUITY_QFLAG vs '...' in path (should be perfectly aligned)"); ax[3].text(0, 1, d.to_string(index=False), family="monospace", va="top")

def d7(ax):
    s = q("SELECT log10(greatest(dur,1)) ld, typ, part FROM t USING SAMPLE 500000 ROWS")
    ax[0].hist(s.ld, bins=80, color=C[0]); ax[0].set_title("log10 TOTAL_DURATION (s)")
    for i, (k, g) in enumerate(s.groupby("typ")): ax[1].hist(g.ld, bins=60, alpha=.5, density=True, label=k, color=C[i % 6])
    ax[1].legend(); ax[1].set_title("Duration by TRANSACTION_TYPE")
    p = q("SELECT part, median(dur) med, quantile_cont(dur,.9) p90 FROM t GROUP BY 1 ORDER BY 1", "d7_part")
    p.set_index("part")[["med", "p90"]].plot.bar(ax=ax[2], logy=True, rot=0)
    ax[2].tick_params(axis="x", labelsize=6)
    ax[2].set_title("Median / P90 duration by participants")
    c = q("SELECT cont, median(dur) med FROM t GROUP BY 1", "d7_cont"); bar(ax[3], c.set_index("cont").med, "Median duration: continuous (Y) vs gap (N)", C[1])

def d8(ax):
    m = q("SELECT oty, bty, count(*) n, median(usd) med FROM t GROUP BY 1,2 ORDER BY 1,2", "d8_types")
    m["k"] = m.oty + ">" + m.bty; bar(ax[0], m.set_index("k").n, "Party-type combinations (count)")
    bar(ax[1], m.set_index("k").med, "Median USD by combination", C[1])
    c = q("SELECT oc, avg((oty='B')::int)*100 b FROM t GROUP BY 1 ORDER BY count(*) DESC LIMIT 15", "d8_business_share_country"); bar(ax[2], c.set_index("oc").b, "% sender=Business by country", C[2])
    t = q("SELECT typ, oty, count(*) n FROM t GROUP BY 1,2", "d8_type")
    t.pivot_table(index="typ", columns="oty", values="n", fill_value=0).pipe(lambda p: p.div(p.sum(1), axis=0)).plot.bar(stacked=True, ax=ax[3], rot=0)
    ax[3].set_title("Sender type mix by routing type")

def d9(ax):
    a = q("SELECT oacc, count(*) n FROM t GROUP BY 1", "d9_acct_freq")
    ax[0].hist(np.log10(a.n), bins=50, color=C[0]); ax[0].set_title("Payments per ordering account (log10) - heavy tail?")
    b = q("SELECT bacc, count(*) n FROM t GROUP BY 1")
    ax[1].hist(np.log10(b.n), bins=50, color=C[1]); ax[1].set_title("Payments per beneficiary account (log10)")
    tk = q(r"""SELECT regexp_extract(otok, '^[^\s,;|]+') tok, count(*) n
               FROM t WHERE otok IS NOT NULL GROUP BY 1 HAVING tok <> '' ORDER BY 2 DESC LIMIT 15""", "d9_first_token")
    bar(ax[2], tk.set_index("tok").n, "Most frequent leading ORDERING token", C[2], True)
    ib = q("SELECT oc, avg((otok LIKE '%iban%')::int)*100 iban FROM t GROUP BY 1 ORDER BY count(*) DESC LIMIT 15", "d9_iban_country")
    bar(ax[3], ib.set_index("oc").iban, "% ordering details containing IBAN token, by sender country", C[4])

def d10(ax):
    a = q("""SELECT anom, count(*) n, median(usd) med_usd, avg((oty='B')::int) b_share, avg(domestic::int) dom, avg(part) part
             FROM t WHERE anom IS NOT NULL GROUP BY 1 ORDER BY n DESC""", "d10_summary")
    bar(ax[0], a.set_index("anom").n, "Anomaly counts", C[3], True)
    s = q("SELECT anom, lusd FROM (SELECT anom, lusd FROM t WHERE anom IS NOT NULL) USING SAMPLE 200000 ROWS")
    for i, (k, g) in enumerate(s.groupby("anom")): ax[1].hist(g.lusd, bins=40, alpha=.5, density=True, label=k, color=C[i % 6])
    ax[1].legend(fontsize=5, loc="upper left", framealpha=0.9)
    ax[1].set_title("log10 USD by anomaly type")
    ratio = q("""WITH m AS (SELECT oacc, median(usd) mu FROM t GROUP BY 1)
                 SELECT a, lr FROM (
                   SELECT coalesce(t.anom,'NONE') a, log10(t.usd / m.mu) lr
                   FROM t JOIN m USING (oacc)
                   WHERE m.mu > 0 AND t.usd > 0
                 ) USING SAMPLE 1000000 ROWS""")
    plotted = False
    for i, (k, g) in enumerate(ratio.groupby("a")):
        if k in ("NONE", "FAT_FINGER_MISTAKE"):
            ax[2].hist(g.lr.clip(-3, 4), bins=60, alpha=.5, density=True, label=k, color=C[i % 6])
            plotted = True
    if plotted: ax[2].legend()
    ax[2].set_title("USD / sender's median USD (log10): fat-finger spike at +1/+2?")
    d = q("""WITH x AS (SELECT oacc,bacc,usd,cur,ts, lag(ts) OVER (PARTITION BY oacc,bacc,usd,cur ORDER BY ts) pts, anom FROM t)
             SELECT coalesce(anom='DUPLICATE_PAYMENT', false) is_dup_label, log10(greatest(epoch(ts)-epoch(pts),1)) lgap
             FROM (SELECT * FROM x WHERE pts IS NOT NULL) USING SAMPLE 300000 ROWS""", "d10_dup_gap")
    for i, (k, g) in enumerate(d.groupby("is_dup_label", dropna=False)): ax[3].hist(g.lgap, bins=50, alpha=.5, density=True, label=f"dup label={k}", color=C[i])
    ax[3].legend(); ax[3].set_title("Time since identical (acct,acct,amount,ccy) payment, log10 s")

PAGES = [("1. Data quality & scale", d1), ("2. Time patterns", d2), ("3. Currency", d3), ("4. Payment value", d4),
         ("5. Routing & corridors", d5), ("6. Path structure", d6), ("7. Duration", d7), ("8. Party types", d8),
         ("9. Party details & accounts", d9), ("10. Anomalies", d10)]

with PdfPages(OUT) as pdf:
    for title, fn in PAGES:
        print("building", title, flush=True)
        try: page(pdf, title, fn)
        except Exception as e:
            print("  !! failed:", type(e).__name__, e, flush=True)  # keep going; fix that page later
print("done ->", OUT, "| aggregates in ./agg/")
