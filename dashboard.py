"""
US Census Workforce Income Analytics — dashboard renderer.

Reads data/adult_census.csv (the REAL UCI Adult / Census Income dataset,
1994 US Census records) and renders ONE polished multi-panel PNG dashboard
(1600x1000 px). Design: slate + coral on soft paper.

Backend: matplotlib Agg. English labels everywhere. Run: python dashboard.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

CSV_PATH = "data/adult_census.csv"

BG, SLATE, SLATE_D, CORAL, CORAL_D, TEAL, GOLD, SOFT = (
    "#FAFAF8", "#475569", "#1E293B", "#E76F51", "#C4553A", "#0E9F8A", "#C9A227", "#E8E4DC")

df = pd.read_csv(CSV_PATH)
hi = df["income"] == ">50K"

def hi50_rate(s):
    return float((s == ">50K").mean() * 100)

n_records = len(df)
pct_hi = hi50_rate(df["income"])
n_hi = int(hi.sum())
med_hours = float(df["hours-per-week"].median())
med_age = float(df["age"].median())
mean_hours_hi = float(df.loc[hi, "hours-per-week"].mean())
mean_hours_lo = float(df.loc[~hi, "hours-per-week"].mean())

df["age_band"] = pd.cut(df["age"], bins=[0, 25, 35, 45, 55, 65, 200],
                        labels=["17–25", "26–35", "36–45", "46–55", "56–65", "66+"])
edu_order = ["Preschool", "1st-4th", "5th-6th", "7th-8th", "9th", "10th", "11th",
             "12th", "HS-grad", "Some-college", "Assoc-voc", "Assoc-acdm",
             "Bachelors", "Masters", "Prof-school", "Doctorate"]

fig = plt.figure(figsize=(16, 10), facecolor=BG)
gs = fig.add_gridspec(3, 3, height_ratios=[0.62, 1, 1], hspace=0.6, wspace=0.42,
                      left=0.06, right=0.965, top=0.88, bottom=0.07)

fig.text(0.06, 0.95, "US CENSUS  •  WORKFORCE INCOME ANALYTICS", fontsize=11, color=CORAL_D, weight="bold", va="center")
fig.text(0.06, 0.915, "1994 Census records  •  who earns over $50K a year?", fontsize=13, color=SLATE_D, va="center")

def kpi_card(pos, label, value, sub=""):
    ax = fig.add_subplot(pos); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.01, 0.04), 0.98, 0.92, boxstyle="round,pad=0.015,rounding_size=0.09",
                                facecolor="white", edgecolor=SOFT, linewidth=1.2, transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.06, 0.86), 0.88, 0.045, boxstyle="round,pad=0.004,rounding_size=0.03",
                                facecolor=CORAL, edgecolor="none", transform=ax.transAxes))
    ax.text(0.5, 0.52, value, ha="center", va="center", fontsize=20, fontweight="bold",
            color=CORAL_D, transform=ax.transAxes)
    ax.text(0.5, 0.30, label, ha="center", va="center", fontsize=9.5, weight="bold",
            color=SLATE_D, transform=ax.transAxes)
    if sub:
        ax.text(0.5, 0.16, sub, ha="center", va="center", fontsize=8, color=SLATE, transform=ax.transAxes)

def style(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(SOFT)
    ax.grid(axis="x", alpha=0.25, linestyle="--"); ax.tick_params(colors=SLATE, labelsize=9)

kpi_card(gs[0, 0], "CENSUS RECORDS", f"{n_records:,}", "train + test combined")
kpi_card(gs[0, 1], "EARNING > $50K / YR", f"{pct_hi:.1f}%", f"{n_hi:,} of {n_records:,}")
kpi_card(gs[0, 2], "MEDIAN AGE", f"{med_age:.0f} yrs", f"median {med_hours:.0f} hrs/week")

# ---- Row 2: education / occupation / sex ----
ax = fig.add_subplot(gs[1, 0]); style(ax)
edu_rate = df.groupby("education")["income"].apply(hi50_rate)
edu_rate = edu_rate.reindex([e for e in edu_order if e in edu_rate.index])
bars = ax.barh(edu_rate.index, edu_rate.values, color=SLATE, height=0.6)
for b, e in zip(bars, edu_rate.index):
    if e in ("Doctorate", "Prof-school"):
        b.set_color(CORAL)
ax.set_title(">50K rate by education", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_xlabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=7.5)

ax = fig.add_subplot(gs[1, 1]); style(ax)
occ_rate = df.groupby("occupation")["income"].apply(hi50_rate).sort_values()
bars = ax.barh(occ_rate.index, occ_rate.values, color=SLATE, height=0.6)
bars[-1].set_color(CORAL)
ax.set_title(">50K rate by occupation", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_xlabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=7.5)

ax = fig.add_subplot(gs[1, 2]); style(ax)
sex_rate = df.groupby("sex")["income"].apply(hi50_rate)
bars = ax.bar(sex_rate.index, sex_rate.values, color=[SLATE, CORAL], width=0.55)
ax.set_title(">50K rate by sex — pay gap", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_ylabel("% earning >$50K", color=SLATE)
for i, v in enumerate(sex_rate.values):
    ax.text(i, v + 0.6, f"{v:.1f}%", ha="center", fontsize=10, weight="bold", color=SLATE_D)
ax.set_ylim(0, sex_rate.values.max() * 1.18)

# ---- Row 3: hours / age band / capital gain ----
ax = fig.add_subplot(gs[2, 0]); style(ax)
ax.hist(df.loc[hi, "hours-per-week"], bins=range(0, 101, 5), color=CORAL, alpha=0.85, label=">$50K")
ax.hist(df.loc[~hi, "hours-per-week"], bins=range(0, 101, 5), color=SLATE, alpha=0.45, label="≤$50K")
ax.set_title("Hours/week by income group", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_xlabel("Hours per week", color=SLATE); ax.set_ylabel("People", color=SLATE)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.text(0.04, 0.90, f">{mean_hours_hi:.1f} vs {mean_hours_lo:.1f} hrs mean", transform=ax.transAxes,
        ha="left", fontsize=8.5, color=SLATE_D,
        bbox=dict(facecolor="white", edgecolor=SOFT, boxstyle="round,pad=0.3"))

ax = fig.add_subplot(gs[2, 1]); style(ax)
age_rate = df.groupby("age_band", observed=True)["income"].apply(hi50_rate)
bars = ax.bar(age_rate.index.astype(str), age_rate.values, color=TEAL, width=0.6)
bars[int(np.argmax(age_rate.values))].set_color(CORAL)
ax.set_title(">50K rate by age band", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_ylabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=8.5)

ax = fig.add_subplot(gs[2, 2]); style(ax)
gain_hi = df.loc[hi & (df["capital-gain"] > 0), "capital-gain"]
gain_lo = df.loc[~hi & (df["capital-gain"] > 0), "capital-gain"]
bins = np.logspace(1, 5.2, 30)
ax.hist(gain_hi, bins=bins, color=CORAL, alpha=0.85, label=">$50K")
ax.hist(gain_lo, bins=bins, color=SLATE, alpha=0.45, label="≤$50K")
ax.set_xscale("log")
ax.set_title("Capital-gain distribution", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=10)
ax.set_xlabel("Capital gain ($) — log scale", color=SLATE); ax.set_ylabel("People", color=SLATE)
ax.legend(fontsize=8.5, frameon=False)

fig.text(0.5, 0.015, "Source: UCI Adult / Census Income dataset (Kohavi & Becker) — real 1994 US Census records",
         ha="center", fontsize=8, color=SLATE)
fig.savefig("dashboard.png", dpi=100, facecolor=BG)
print("saved dashboard.png", df.shape, f">{pct_hi:.1f}% earn >50K")
