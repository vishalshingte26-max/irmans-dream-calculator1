import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

# ---------------- HEADER ----------------
st.title("IRMAN'S DREAM CALCULATOR")

st.markdown(
    """
This tool helps you understand where life stress comes from  
and how your money can be allocated in the best possible way.

Step 1 diagnoses stress  
Step 2 optimizes your plan  
You can download your report at the end
"""
)

st.markdown("---")

# ---------------- TIME HORIZON ----------------
horizon_years = st.slider("Planning horizon (years)", 5, 30, 10)

# ---------------- INCOME ----------------
salary = st.number_input("Monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Unavoidable monthly expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.warning("Please enter income")
    st.stop()

base_surplus = salary - expenses
if base_surplus <= 0:
    st.error("Expenses exceed income")
    st.stop()

# ---------------- LIFE ASSUMPTIONS ----------------
career = st.selectbox("Career satisfaction", ["High", "Moderate", "Low"])
health = st.selectbox("Health routine", ["Good", "Irregular", "Poor"])
work = st.selectbox("Work style", ["Balanced", "Aggressive", "Frequent burnout"])

income_penalty = 0
if career == "Moderate":
    income_penalty += 0.05
elif career == "Low":
    income_penalty += 0.12

if health == "Irregular":
    income_penalty += 0.05
elif health == "Poor":
    income_penalty += 0.10

if work == "Aggressive":
    income_penalty -= 0.08
elif work == "Frequent burnout":
    income_penalty += 0.12

adjusted_surplus = base_surplus * (1 - income_penalty)

# ---------------- GOALS ----------------
goals = {
    "Asset creation": st.number_input("Assets goal ₹", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund ₹", 0, step=50000),
    "Education / loan": st.number_input("Education or loan ₹", 0, step=50000),
    "Marriage & family": st.number_input("Marriage & family ₹", 0, step=50000),
    "Social contribution": st.number_input("Social contribution ₹", 0, step=20000),
}

# ---------------- IMPORTANCE ----------------
weights = {}
for g in goals:
    weights[g] = st.slider(f"Importance of {g}", 1, 5, 3)

# ---------------- STAGE 1 ----------------
if st.button("1️⃣ Show stress diagnosis"):

    feasible_capacity = adjusted_surplus * 12 * horizon_years
    equal_share = feasible_capacity / len(goals)

    stress_before = {}
    total_stress_before = 0

    for g in goals:
        gap = max(goals[g] - equal_share, 0)
        stress_before[g] = gap * weights[g]
        total_stress_before += stress_before[g]

    st.session_state["feasible_capacity"] = feasible_capacity
    st.session_state["stress_before"] = stress_before
    st.session_state["total_stress_before"] = total_stress_before

    fig, ax = plt.subplots()
    ax.bar(stress_before.keys(), stress_before.values())
    ax.set_title("Stress before optimization")
    plt.xticks(rotation=30)
    st.pyplot(fig)

# ---------------- STAGE 2 ----------------
if st.button("2️⃣ Optimize my plan"):

    if "feasible_capacity" not in st.session_state:
        st.warning("Run diagnosis first")
        st.stop()

    remaining = st.session_state["feasible_capacity"]
    optimized = {}
    stress_after = {}
    total_stress_after = 0

    sorted_goals = sorted(goals, key=lambda g: weights[g], reverse=True)

    for g in sorted_goals:
        alloc = min(goals[g], remaining)
        optimized[g] = alloc
        shortfall = goals[g] - alloc
        stress_after[g] = shortfall * weights[g]
        total_stress_after += stress_after[g]
        remaining -= alloc

    improvement = (
        (st.session_state["total_stress_before"] - total_stress_after)
        / st.session_state["total_stress_before"] * 100
        if st.session_state["total_stress_before"] > 0 else 0
    )

    st.success(f"Life stress reduced by {improvement:.1f}%")

    # ---------------- SAVE DATA ----------------
    record = {
        "timestamp": datetime.now(),
        "salary": salary,
        "expenses": expenses,
        "adjusted_surplus": adjusted_surplus,
        "horizon_years": horizon_years,
        "stress_before": st.session_state["total_stress_before"],
        "stress_after": total_stress_after,
        "improvement_percent": improvement
    }

    for g in goals:
        record[f"goal_{g}"] = goals[g]
        record[f"weight_{g}"] = weights[g]
        record[f"allocated_{g}"] = optimized[g]

    df = pd.DataFrame([record])

    if not os.path.exists("responses.csv"):
        df.to_csv("responses.csv", index=False)
    else:
        df.to_csv("responses.csv", mode="a", header=False, index=False)

    # ---------------- DOWNLOAD ----------------
    st.subheader("Download your report")

    st.download_button(
        label="Download my life plan report",
        data=df.to_csv(index=False),
        file_name="my_life_plan_report.csv",
        mime="text/csv"
    )
