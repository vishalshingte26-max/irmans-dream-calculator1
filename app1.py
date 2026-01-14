import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

st.title("IRMAN'S DREAM CALCULATOR")

st.markdown("""
This tool helps you understand **how everyday life choices quietly affect your long-term goals**.

You will:
1. Answer simple life questions  
2. See where stress comes from  
3. Ask the model to optimally allocate your money  
4. See how much stress the model reduces  

Nothing is forced. The model only shows trade-offs.
""")

st.markdown("---")

# =========================
# PLANNING HORIZON
# =========================
st.subheader("1️⃣ Time horizon")

st.markdown("""
**Why this matters:**  
More time reduces pressure. Short timelines increase stress.
""")

horizon_years = st.slider(
    "For how many years are you planning your major life goals?",
    5, 30, 10
)

st.markdown("---")

# =========================
# INCOME & EXPENSES
# =========================
st.subheader("2️⃣ Income and basic expenses")

st.markdown("""
**Income** is what supports all dreams.  
**Unavoidable expenses** cannot be compromised (rent, food, utilities).
""")

salary = st.number_input("Your monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Your unavoidable monthly expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.warning("Income is required to continue")
    st.stop()

base_surplus = salary - expenses

if base_surplus <= 0:
    st.error("Your expenses exceed income. No surplus is available for goals.")
    st.stop()

st.success(f"Money available for goals every month: ₹{base_surplus:,.0f}")

st.markdown("---")

# =========================
# LIFE CONDITIONS
# =========================
st.subheader("3️⃣ Life conditions (these quietly change money availability)")

st.markdown("""
These questions reflect **real-world frictions**.
The model explains every penalty clearly.
""")

# Job stability
job = st.selectbox(
    "Job stability and satisfaction",
    [
        "Stable and satisfying (no penalty)",
        "Somewhat unstable (5% income loss)",
        "Highly unstable or stressful (12% income loss)"
    ]
)

st.caption("Unstable jobs reduce effective savings due to stress, switching costs and uncertainty.")

# Health
health = st.selectbox(
    "Health and daily routine",
    [
        "Good sleep and regular exercise (no penalty)",
        "Irregular routine (5% income loss)",
        "Poor health habits (10% income loss)"
    ]
)

st.caption("Poor health increases medical costs and reduces productivity over time.")

# AQI
aqi = st.selectbox(
    "Air quality where you live",
    [
        "Mostly good AQI (no extra expense)",
        "Moderate AQI (4% expense increase)",
        "Poor AQI most of the year (8% expense increase)"
    ]
)

st.caption("Poor air quality leads to higher medical and lifestyle expenses.")

# Family setup
family = st.selectbox(
    "Living arrangement",
    [
        "Living with family (5% lower expenses)",
        "Living away from family (5% higher expenses)"
    ]
)

st.caption("Living alone usually increases rent, food and support costs.")

# Work style
work = st.selectbox(
    "Work style",
    [
        "Balanced and sustainable (no penalty)",
        "Aggressive long hours (8% short-term income boost)",
        "Frequent burnout cycles (12% income loss)"
    ]
)

st.caption("Overwork may boost income short-term but burnout reduces long-term savings.")

# =========================
# APPLY IMPACTS
# =========================
income_penalty = 0
expense_penalty = 0

if "Somewhat" in job:
    income_penalty += 0.05
elif "Highly" in job:
    income_penalty += 0.12

if "Irregular" in health:
    income_penalty += 0.05
elif "Poor" in health:
    income_penalty += 0.10

if "Moderate" in aqi:
    expense_penalty += 0.04
elif "Poor" in aqi:
    expense_penalty += 0.08

if "with family" in family:
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

if "Aggressive" in work:
    income_penalty -= 0.08
elif "burnout" in work.lower():
    income_penalty += 0.12

adjusted_surplus = base_surplus * (1 - income_penalty) * (1 - expense_penalty)

st.info(f"Usable monthly surplus after life effects: ₹{adjusted_surplus:,.0f}")

st.markdown("---")

# =========================
# GOALS
# =========================
st.subheader("4️⃣ Your life goals")

st.markdown("""
Enter the **total amount** you want to spend on each goal over the planning period.
""")

goals = {
    "Asset creation": st.number_input("House / land / vehicle (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education or loan repayment (₹)", 0, step=50000),
    "Marriage & family setup": st.number_input("Marriage & family setup (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution / giving (₹)", 0, step=20000),
}

# =========================
# IMPORTANCE
# =========================
st.subheader("5️⃣ Importance of each goal")

st.markdown("""
Importance shows **how stressful it would be if this goal is delayed**.

Higher percentage = higher protection during optimization.
""")

importance = {}
for g in goals:
    importance[g] = st.slider(f"{g} importance (%)", 10, 100, 50)

st.markdown("---")

# =========================
# STRESS DIAGNOSIS
# =========================
if st.button("1️⃣ Show where stress comes from"):

    feasible_capacity = adjusted_surplus * 12 * horizon_years
    equal_share = feasible_capacity / len(goals)

    stress_before = {}
    total_stress_before = 0

    for g in goals:
        gap = max(goals[g] - equal_share, 0)
        stress_before[g] = gap * importance[g]
        total_stress_before += stress_before[g]

    st.session_state.update({
        "feasible_capacity": feasible_capacity,
        "stress_before": stress_before,
        "total_stress_before": total_stress_before
    })

    st.subheader("Stress before optimization")

    fig, ax = plt.subplots()
    ax.bar(stress_before.keys(), stress_before.values())
    ax.set_ylabel("Stress units")
    plt.xticks(rotation=30)
    st.pyplot(fig)

    st.info(f"Total life stress score: {total_stress_before:,.0f}")

# =========================
# OPTIMIZATION
# =========================
if st.button("2️⃣ Optimize my life plan"):

    if "feasible_capacity" not in st.session_state:
        st.warning("Please run stress diagnosis first")
        st.stop()

    feasible_capacity = st.session_state["feasible_capacity"]
    MIN_PERCENT = 0.35

    optimized = {}
    remaining = feasible_capacity

    # Minimum allocation
    for g in goals:
        alloc = min(goals[g] * MIN_PERCENT, remaining)
        optimized[g] = alloc
        remaining -= alloc

    # Priority allocation
    for g in sorted(goals, key=lambda x: importance[x], reverse=True):
        if remaining <= 0:
            break
        extra = min(goals[g] - optimized[g], remaining)
        optimized[g] += extra
        remaining -= extra

    stress_after = {}
    total_stress_after = 0

    for g in goals:
        shortfall = max(goals[g] - optimized[g], 0)
        stress_after[g] = shortfall * importance[g]
        total_stress_after += stress_after[g]

    improvement = (
        (st.session_state["total_stress_before"] - total_stress_after)
        / st.session_state["total_stress_before"] * 100
    )

    st.subheader("Optimized outcome")

    for g in goals:
        st.write(
            f"{g}: ₹{optimized[g]:,.0f} "
            f"({optimized[g]/goals[g]*100:.1f}% of target)"
        )

    st.success(f"Total life stress reduced by {improvement:.1f}%")

    # Save data
    record = {
        "timestamp": datetime.now(),
        "stress_before": st.session_state["total_stress_before"],
        "stress_after": total_stress_after,
        "improvement_percent": improvement
    }

    for g in goals:
        record[f"goal_{g}"] = goals[g]
        record[f"importance_{g}"] = importance[g]
        record[f"allocated_{g}"] = optimized[g]

    df = pd.DataFrame([record])

    if not os.path.exists("responses.csv"):
        df.to_csv("responses.csv", index=False)
    else:
        df.to_csv("responses.csv", mode="a", header=False, index=False)

    st.download_button(
        "Download my optimized life report",
        df.to_csv(index=False),
        file_name="my_life_plan_report.csv",
        mime="text/csv"
    )
