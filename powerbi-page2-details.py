# ============================================================
# Power BI Python visual — PAGE 2: Details
# صفحة 2: التفاصيل — US Census Workforce Income Analytics
# ------------------------------------------------------------
# HOW TO USE / طريقة الاستخدام:
#  1) Get Data → load data/adult_census.csv (نفس الجدول)
#  2) Insert → Python visual (صفحة جديدة اسمها "Details")
#  3) Drag these EXACT 5 columns into the visual's Values well /
#     اسحب هذه الأعمدة الخمسة بالضبط إلى خانة Values:
#        - income
#        - sex
#        - hours-per-week
#        - age
#        - capital-gain
#  4) Paste this entire script / الصق هذا السكربت كاملاً
#
# Uses ONLY the `dataset` DataFrame injected by Power BI.
# No file loading, no plt.show() — Power BI renders the figure.
# Design: slate + coral on soft paper.
# ============================================================
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

REQUIRED = ["income", "sex", "hours-per-week", "age", "capital-gain"]
missing = [c for c in REQUIRED if c not in dataset.columns]
if missing:
    raise ValueError("Missing columns — drag into Values: " + ", ".join(missing))

df = dataset.dropna(subset=REQUIRED).copy()
hi = df["income"] == ">50K"
df["age_band"] = pd.cut(df["age"], bins=[0, 25, 35, 45, 55, 65, 200],
                        labels=["17–25", "26–35", "36–45", "46–55", "56–65", "66+"])

BG, SLATE, SLATE_D, CORAL, CORAL_D, TEAL, SOFT = (
    "#FAFAF8", "#475569", "#1E293B", "#E76F51", "#C4553A", "#0E9F8A", "#E8E4DC")

fig = plt.figure(figsize=(13, 8), facecolor=BG)
gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.4, left=0.08, right=0.95, top=0.88, bottom=0.1)
fig.text(0.08, 0.95, "DETAILS  •  WORKFORCE INCOME", fontsize=11, color=CORAL_D, weight="bold", va="center")

def style(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(SOFT)
    ax.grid(axis="y", alpha=0.25, linestyle="--"); ax.tick_params(colors=SLATE, labelsize=9)

ax = fig.add_subplot(gs[0, 0]); style(ax)
sex_rate = ((df["income"] == ">50K").groupby(df["sex"]).mean() * 100)
bars = ax.bar(sex_rate.index, sex_rate.values, color=[SLATE, CORAL], width=0.55)
ax.set_title(">50K rate by sex — pay gap", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_ylabel("% earning >$50K", color=SLATE)
for i, v in enumerate(sex_rate.values):
    ax.text(i, v + 0.6, f"{v:.1f}%", ha="center", fontsize=10, weight="bold", color=SLATE_D)
ax.set_ylim(0, sex_rate.values.max() * 1.18)

ax = fig.add_subplot(gs[0, 1]); style(ax)
ax.hist(df.loc[hi, "hours-per-week"], bins=range(0, 101, 5), color=CORAL, alpha=0.85, label=">$50K")
ax.hist(df.loc[~hi, "hours-per-week"], bins=range(0, 101, 5), color=SLATE, alpha=0.45, label="≤$50K")
ax.set_title("Hours/week by income group", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_xlabel("Hours per week", color=SLATE); ax.set_ylabel("People", color=SLATE)
ax.legend(fontsize=9, frameon=False)

ax = fig.add_subplot(gs[1, 0]); style(ax)
age_rate = ((df["income"] == ">50K").groupby(df["age_band"], observed=True).mean() * 100)
bars = ax.bar(age_rate.index.astype(str), age_rate.values, color=TEAL, width=0.6)
bars[int(np.argmax(age_rate.values))].set_color(CORAL)
ax.set_title(">50K rate by age band", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_ylabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=8.5)

ax = fig.add_subplot(gs[1, 1]); style(ax)
gain_hi = df.loc[hi & (df["capital-gain"] > 0), "capital-gain"]
gain_lo = df.loc[~hi & (df["capital-gain"] > 0), "capital-gain"]
bins = np.logspace(1, 5.2, 30)
ax.hist(gain_hi, bins=bins, color=CORAL, alpha=0.85, label=">$50K")
ax.hist(gain_lo, bins=bins, color=SLATE, alpha=0.45, label="≤$50K")
ax.set_xscale("log")
ax.set_title("Capital-gain distribution", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_xlabel("Capital gain ($) — log scale", color=SLATE); ax.set_ylabel("People", color=SLATE)
ax.legend(fontsize=9, frameon=False)
