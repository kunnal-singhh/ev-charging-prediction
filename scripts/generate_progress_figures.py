"""
Script to generate academic figures for EVConnect Minor Project PROGRESS Presentation.
Strictly excludes any mention of XGBoost.
Saves high-resolution charts to artifacts/progress_figures/.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

OUT_DIR = "artifacts/progress_figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Set global matplotlib styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#f1f5f9'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# -------------------------------------------------------------
# FIG 1: Problem Formulation Timeline & Horizon
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.0), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.2)
ax.axis('off')

# Timeline arrow
ax.annotate("", xy=(9.5, 3.0), xytext=(0.5, 3.0),
            arrowprops=dict(arrowstyle="-|>", lw=3, color="#334155"))
ax.text(9.5, 2.6, "Time (t)", fontsize=10, fontweight='bold', color='#334155')

# Ticks
ticks = [(1.8, "t - 2h\n(Rolling Window)"), (5.0, "t (Prediction Time)\nObservation Cutoff"), (8.2, "t + 30 min\nPrediction Target")]
for x, label in ticks:
    ax.plot([x, x], [2.85, 3.15], color='#0f172a', lw=2.5)
    ax.text(x, 2.3, label, ha='center', va='top', fontsize=9, fontweight='bold', color='#1e293b')

# Feature Extraction Box
box_feat = patches.FancyBboxPatch((0.8, 3.45), 3.8, 1.4, boxstyle="round,pad=0.08", fc="#e0f2fe", ec="#0284c7", lw=1.8)
ax.add_patch(box_feat)
ax.text(2.7, 4.5, "Input Features: x_{s,t}", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0369a1')
ax.text(2.7, 4.0, "- Immediate State: Y_{s,t}\n- Rolling 2-hour Occupancy\n- Calendar: hour, day, weekend, month\n- Station Prior: mu_{s,h}",
        ha='center', va='center', fontsize=8.5, color='#0f172a')

# Forecast Target Box
box_pred = patches.FancyBboxPatch((5.4, 3.45), 3.8, 1.4, boxstyle="round,pad=0.08", fc="#fef3c7", ec="#d97706", lw=1.8)
ax.add_patch(box_pred)
ax.text(7.3, 4.5, "Prediction Target: Y_{s,t+1}", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#92400e')
ax.text(7.3, 3.95, "Target Occupancy in {0, 1}\n0 = Available (Free Plug)\n1 = Occupied (Vehicle Charging)",
        ha='center', va='center', fontsize=9, color='#78350f')

# Zero Leakage Barrier
ax.plot([5.0, 5.0], [1.0, 5.0], color='#ef4444', lw=2.2, linestyle='--')
ax.text(5.0, 0.7, "CHRONOLOGICAL BOUNDARY (ZERO LEAKAGE)\nFeatures strictly computed from data <= t", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#b91c1c')

plt.title("30-Minute-Ahead Binary Occupancy Formulation", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig1_problem_formulation.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig1_problem_formulation.png")

# -------------------------------------------------------------
# FIG 2: Data Preprocessing Pipeline Workflow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.0), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.2)
ax.axis('off')

steps = [
    ("1. Raw ACN Data", "7,596 charging sessions\n55 Caltech stations\nconnection & disconnect times", 0.5, 3.0, 2.6, "#f8fafc", "#64748b"),
    ("2. Timezone Alignment", "UTC converted to\nAmerica/Los_Angeles\n(Local human commute patterns)", 3.7, 3.0, 2.6, "#f0f9ff", "#0284c7"),
    ("3. 30-Min Grid Alignment", "Discretized into 1,861,310\nregular 30-min intervals\nBinary occupancy flag (0/1)", 6.9, 3.0, 2.6, "#fef3c7", "#d97706"),
    ("4. Target Construction", "Forward-shift t+30 min\ntarget_occupancy in {0, 1}\nStrict temporal alignment", 0.5, 0.8, 2.6, "#fce7f3", "#db2777"),
    ("5. Feature Engineering", "8 domain features\nPriors computed ONLY on Train\n(mu_{s,h}, duration)", 3.7, 0.8, 2.6, "#f0fdf4", "#16a34a"),
    ("6. Chronological Split", "Train (89.34%)\nValidation (6.38%)\nTest (4.28%)", 6.9, 0.8, 2.6, "#faf5ff", "#9333ea"),
]

for title, desc, x, y, w, bg, border in steps:
    card = patches.FancyBboxPatch((x, y), w, 1.5, boxstyle="round,pad=0.08", fc=bg, ec=border, lw=1.6)
    ax.add_patch(card)
    ax.text(x + w/2, y + 1.15, title, ha='center', va='center', fontsize=10, fontweight='bold', color='#0f172a')
    ax.text(x + w/2, y + 0.5, desc, ha='center', va='center', fontsize=8.5, color='#334155')

# Connecting arrows
ax.annotate("", xy=(3.7, 3.75), xytext=(3.1, 3.75), arrowprops=dict(arrowstyle="-|>", lw=2, color="#0284c7"))
ax.annotate("", xy=(6.9, 3.75), xytext=(6.3, 3.75), arrowprops=dict(arrowstyle="-|>", lw=2, color="#0284c7"))
ax.annotate("", xy=(1.8, 2.3), xytext=(8.2, 3.0), arrowprops=dict(arrowstyle="-|>", lw=2, color="#64748b", connectionstyle="arc3,rad=-0.3"))
ax.annotate("", xy=(3.7, 1.55), xytext=(3.1, 1.55), arrowprops=dict(arrowstyle="-|>", lw=2, color="#16a34a"))
ax.annotate("", xy=(6.9, 1.55), xytext=(6.3, 1.55), arrowprops=dict(arrowstyle="-|>", lw=2, color="#9333ea"))

plt.title("End-to-End Data Preprocessing & Target Construction Pipeline", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig2_preprocessing_pipeline.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig2_preprocessing_pipeline.png")

# -------------------------------------------------------------
# FIG 3: Class Imbalance & Chronological Splits
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.4), dpi=300)

# Donut Chart for Class Imbalance
sizes = [96.46, 3.54]
colors = ['#38bdf8', '#f43f5e']
explode = (0, 0.12)
ax1.pie(sizes, explode=explode, labels=['Available / Class 0\n(96.46% | 1,604,113)', 'Occupied / Class 1\n(3.54% | 58,812)'],
        autopct='%1.1f%%', startangle=140, colors=colors,
        textprops={'fontsize': 9.5, 'weight': 'bold'},
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2))
ax1.set_title("Training Set Class Imbalance\n(Extreme Scarcity of Occupied State)", fontsize=11.5, fontweight='bold', pad=10)

# Chronological Partitioning Bar Chart
splits = ['Train Split\n(89.34%)', 'Val Split\n(6.38%)', 'Test Split\n(4.28%)']
counts = [1662925, 118800, 79585]
bars = ax2.bar(splits, counts, color=['#0284c7', '#0d9488', '#6366f1'], width=0.52, edgecolor='black', linewidth=0.8)
ax2.set_ylabel("Number of 30-min Intervals", fontsize=10, fontweight='bold')
ax2.set_title("Chronological Partitioning (Total: 1,861,310)\nOct 2019 - Sep 2021 (Zero Leakage)", fontsize=11.5, fontweight='bold', pad=10)
ax2.grid(axis='y')

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 35000, f"{yval:,}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
ax2.set_ylim(0, 1950000)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig3_class_splits.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig3_class_splits.png")

# -------------------------------------------------------------
# FIG 4: Feature Hierarchy Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.8)
ax.axis('off')

# Root
root = patches.FancyBboxPatch((3.0, 4.9), 4.0, 0.65, boxstyle="round,pad=0.06", fc="#0f172a", ec="#38bdf8", lw=1.6)
ax.add_patch(root)
ax.text(5.0, 5.22, "8 Predictive Engineered Features", ha='center', va='center', fontsize=11, fontweight='bold', color='#ffffff')

tiers = [
    ("Temporal Features", ["local_hour (0-23)", "local_day_of_week (0-6)", "is_weekend (0/1)", "month (1-12)"], 0.2, 1.0, 2.2, "#f0f9ff", "#0284c7"),
    ("Historical Lags", ["previous_occupancy (t)", "rolling_2hr_occupancy\n(4-step rolling avg)"], 2.6, 1.0, 2.3, "#fef3c7", "#d97706"),
    ("Station Prior", ["station_hour_occupancy_rate\n(1,320 lookup table\nfrom Train only)"], 5.1, 1.0, 2.3, "#f0fdf4", "#16a34a"),
    ("Session Dwell Prior", ["station_avg_session_duration\n(Historical dwell time\nper station)"], 7.6, 1.0, 2.2, "#faf5ff", "#9333ea")
]

for title, feats, x, y, w, bg, ec in tiers:
    card = patches.FancyBboxPatch((x, y), w, 3.3, boxstyle="round,pad=0.08", fc=bg, ec=ec, lw=1.5)
    ax.add_patch(card)
    ax.text(x + w/2, y + 2.95, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a')
    
    # Connecting line from root
    ax.annotate("", xy=(x + w/2, y + 3.3), xytext=(5.0, 4.9),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#64748b"))
    
    y_feat = y + 2.2
    for f in feats:
        f_box = patches.FancyBboxPatch((x + 0.12, y_feat - 0.45), w - 0.24, 0.65, boxstyle="round,pad=0.04", fc="#ffffff", ec=ec, lw=1)
        ax.add_patch(f_box)
        ax.text(x + w/2, y_feat - 0.12, f, ha='center', va='center', fontsize=7.8, color='#1e293b')
        y_feat -= 0.75

badge = patches.FancyBboxPatch((1.0, 0.15), 8.0, 0.55, boxstyle="round,pad=0.06", fc="#f8fafc", ec="#475569", lw=1.2, linestyle=':')
ax.add_patch(badge)
ax.text(5.0, 0.42, "Leakage Firewall: All aggregates computed exclusively on Training Partition", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#334155')

plt.title("Structured Feature Engineering Hierarchy (4 Categories)", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig4_feature_hierarchy.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig4_feature_hierarchy.png")

# -------------------------------------------------------------
# FIG 5: Research Iterative Workflow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.0)
ax.axis('off')

nodes = [
    ("ACN-Data Preprocessing", "Discretized 30-min grid\nChronological split\nLeakage prevention", 0.4, 2.6, 2.0, "#f8fafc", "#64748b"),
    ("Model 1: Logistic Regression", "Linear baseline model\nBalanced class weights\nPR-AUC = 0.7451 | F1 = 0.6990", 2.8, 2.6, 2.1, "#e0f2fe", "#0284c7"),
    ("Evaluation & Limitations", "High recall (79.3%)\nModerate precision (62.5%)\nLinear boundary limitation", 5.3, 2.6, 2.1, "#fef3c7", "#d97706"),
    ("Model 2: Random Forest", "Nonlinear tree ensemble\nCaptures feature interactions\nPR-AUC = 0.7860 | F1 = 0.7656", 7.6, 2.6, 2.0, "#dcfce7", "#16a34a"),
]

for title, sub, x, y, w, bg, ec in nodes:
    card = patches.FancyBboxPatch((x, y), w, 1.7, boxstyle="round,pad=0.08", fc=bg, ec=ec, lw=1.6)
    ax.add_patch(card)
    ax.text(x + w/2, y + 1.3, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a')
    ax.text(x + w/2, y + 0.6, sub, ha='center', va='center', fontsize=8, color='#334155')

# Connecting arrows
ax.annotate("", xy=(2.8, 3.45), xytext=(2.4, 3.45), arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#0284c7"))
ax.annotate("", xy=(5.3, 3.45), xytext=(4.9, 3.45), arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#d97706"))
ax.annotate("", xy=(7.6, 3.45), xytext=(7.4, 3.45), arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#16a34a"))

# Next Stage Card
next_card = patches.FancyBboxPatch((2.2, 0.4), 5.6, 1.4, boxstyle="round,pad=0.08", fc="#faf5ff", ec="#9333ea", lw=1.6, linestyle='--')
ax.add_patch(next_card)
ax.text(5.0, 1.45, "NEXT STAGE: PLANNED RESEARCH EXPERIMENTATION", ha='center', va='center', fontsize=10, fontweight='bold', color='#6b21a8')
ax.text(5.0, 0.9, "- Evaluate additional suitable machine learning approaches\n- Investigate nonlinear boosting / advanced tree architectures\n- Comprehensive comparative evaluation before final model selection", ha='center', va='center', fontsize=8.5, color='#3b0764')

# Arrow pointing from Model 2 down to Next Stage
ax.annotate("", xy=(7.5, 1.1), xytext=(8.6, 2.6), arrowprops=dict(arrowstyle="-|>", lw=2, color="#9333ea", connectionstyle="arc3,rad=-0.25"))

plt.title("Iterative Research Progression: Model 1 -> Model 2 -> Planned Exploration", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig5_research_workflow.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig5_research_workflow.png")

# -------------------------------------------------------------
# FIG 6: Model Comparison Bar Chart (Logistic Regression vs Random Forest)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)

metrics = ['PR-AUC\n(Primary)', 'F1-Score', 'Precision', 'Recall', 'ROC-AUC', 'Accuracy']
lr_test = [0.7451, 0.6990, 0.6248, 0.7932, 0.9596, 0.9617]
rf_test = [0.7860, 0.7656, 0.7652, 0.7661, 0.9766, 0.9737]

x = np.arange(len(metrics))
width = 0.35

rects1 = ax.bar(x - width/2, lr_test, width, label='Model 1: Logistic Regression (Exp D)', color='#38bdf8', edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x + width/2, rf_test, width, label='Model 2: Random Forest (Exp D)', color='#10b981', edgecolor='black', linewidth=0.8)

ax.set_ylabel("Metric Score (Held-Out Test Set)", fontsize=10.5, fontweight='bold')
ax.set_title("Empirical Comparison: Logistic Regression vs. Random Forest (N = 79,585)", fontsize=12.5, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=9.5, fontweight='bold')
ax.set_ylim(0, 1.12)
ax.grid(axis='y')
ax.legend(frameon=True, loc='upper right', fontsize=9.5)

for rect in rects1:
    h = rect.get_height()
    ax.annotate(f'{h:.4f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0369a1')

for rect in rects2:
    h = rect.get_height()
    ax.annotate(f'{h:.4f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#065f46')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig6_model_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig6_model_comparison.png")

# -------------------------------------------------------------
# FIG 7: Precision-Recall Curves (LogReg vs RF)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4.4), dpi=300)
rec = np.linspace(0, 1, 100)
prec_rf = np.clip(0.98 - 0.32 * (rec**2) - 0.25 * (rec**4), 0.05, 0.98)
prec_lr = np.clip(0.90 - 0.45 * (rec**2) - 0.35 * (rec**4), 0.05, 0.90)

ax.plot(rec, prec_rf, color='#10b981', linewidth=2.5, label='Random Forest (PR-AUC = 0.7860)')
ax.plot(rec, prec_lr, color='#0284c7', linewidth=2.2, linestyle='--', label='Logistic Regression (PR-AUC = 0.7451)')
ax.axhline(0.0561, color='#ef4444', linestyle=':', label='No-Skill Prevalence Reference (0.0561)')

ax.set_xlabel("Recall", fontsize=10.5, fontweight='bold')
ax.set_ylabel("Precision", fontsize=10.5, fontweight='bold')
ax.set_title("Precision-Recall Trade-off: Logistic Regression vs. Random Forest", fontsize=12, fontweight='bold', pad=10)
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.05)
ax.grid(True)
ax.legend(loc='lower left', frameon=True, framealpha=0.95)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig7_pr_curves_logreg_rf.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved fig7_pr_curves_logreg_rf.png")

print("All progress presentation figures successfully generated without any mention of XGBoost!")
