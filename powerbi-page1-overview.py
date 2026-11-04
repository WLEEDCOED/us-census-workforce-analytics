# ============================================================
# Power BI Python visual — PAGE 1: Overview
# صفحة 1: نظرة عامة — US Census Workforce Income Analytics
# ------------------------------------------------------------
# HOW TO USE / طريقة الاستخدام:
#  1) Get Data → load data/adult_census.csv
#  2) Insert → Python visual (صفحة جديدة اسمها "Overview")
#  3) Drag these EXACT 5 columns into the visual's Values well /
#     اسحب هذه الأعمدة الخمسة بالضبط إلى خانة Values:
#        - income
#        - age
#        - hours-per-week
#        - education
#        - occupation
#  4) Paste this entire script / الصق هذا السكربت كاملاً
#
# Uses ONLY the `dataset` DataFrame injected by Power BI.
# No file loading, no plt.show() — Power BI renders the figure.
# Design: slate + coral on soft paper.
# ============================================================
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

REQUIRED = ["income", "age", "hours-per-week", "education", "occupation"]
missing = [c for c in REQUIRED if c not in dataset.columns]
if missing:
    raise ValueError("Missing columns — drag into Values: " + ", ".join(missing))

df = dataset.dropna(subset=REQUIRED).copy()
hi = df["income"] == ">50K"
pct_hi = float(hi.mean() * 100)

BG, SLATE, SLATE_D, CORAL, CORAL_D, SOFT = "#FAFAF8", "#475569", "#1E293B", "#E76F51", "#C4553A", "#E8E4DC"

fig = plt.figure(figsize=(13, 8), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[0.55, 1], hspace=0.5, wspace=0.4,
                      left=0.08, right=0.95, top=0.88, bottom=0.1)
fig.text(0.08, 0.95, "OVERVIEW  •  WORKFORCE INCOME", fontsize=11, color=CORAL_D, weight="bold", va="center")

def kpi_card(pos, label, value, sub=""):
    ax = fig.add_subplot(pos); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.01, 0.04), 0.98, 0.92, boxstyle="round,pad=0.015,rounding_size=0.09",
                                facecolor="white", edgecolor=SOFT, linewidth=1.2, transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0.06, 0.86), 0.88, 0.045, boxstyle="round,pad=0.004,rounding_size=0.03",
                                facecolor=CORAL, edgecolor="none", transform=ax.transAxes))
    ax.text(0.5, 0.52, value, ha="center", va="center", fontsize=19, fontweight="bold",
            color=CORAL_D, transform=ax.transAxes)
    ax.text(0.5, 0.30, label, ha="center", va="center", fontsize=9, weight="bold",
            color=SLATE_D, transform=ax.transAxes)
    if sub:
        ax.text(0.5, 0.16, sub, ha="center", va="center", fontsize=8, color=SLATE, transform=ax.transAxes)

def style(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(SOFT)
    ax.grid(axis="x", alpha=0.25, linestyle="--"); ax.tick_params(colors=SLATE, labelsize=9)

kpi_card(gs[0, 0], "CENSUS RECORDS", f"{len(df):,}")
kpi_card(gs[0, 1], "EARNING > $50K / YR", f"{pct_hi:.1f}%", f"{int(hi.sum()):,} people")

edu_order = ["Preschool", "1st-4th", "5th-6th", "7th-8th", "9th", "10th", "11th", "12th",
             "HS-grad", "Some-college", "Assoc-voc", "Assoc-acdm", "Bachelors", "Masters",
             "Prof-school", "Doctorate"]
ax = fig.add_subplot(gs[1, 0]); style(ax)
edu_rate = (df["income"] == ">50K").groupby(df["education"]).mean() * 100
edu_rate = edu_rate.reindex([e for e in edu_order if e in edu_rate.index])
bars = ax.barh(edu_rate.index, edu_rate.values, color=SLATE, height=0.6)
for b, e in zip(bars, edu_rate.index):
    if e in ("Doctorate", "Prof-school"): b.set_color(CORAL)
ax.set_title(">50K rate by education", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_xlabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=7.5)

ax = fig.add_subplot(gs[1, 1]); style(ax)
occ_rate = ((df["income"] == ">50K").groupby(df["occupation"]).mean() * 100).sort_values()
bars = ax.barh(occ_rate.index, occ_rate.values, color=SLATE, height=0.6)
bars[-1].set_color(CORAL)
ax.set_title(">50K rate by occupation", loc="left", fontsize=12, fontweight="bold", color=SLATE_D, pad=8)
ax.set_xlabel("% earning >$50K", color=SLATE); ax.tick_params(labelsize=7.5)
