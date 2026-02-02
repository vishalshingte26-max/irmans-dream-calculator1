import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ================= PAGE CONFIG =================
st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

# ================= TITLE =================
st.title("IRMAN'S DREAM CALCULATOR")

st.markdown(
    """
### Constraint-Based Life Planning Model

This tool shows how life goals interact with limited income and lifestyle constraints.
It is designed to understand **aspirations vs feasibility**, not to judge choices.
"""
)

st.markdown("---")

# ================= PLANNING HORIZON =================
st.subheader("1️⃣ Planning horizon")

horizon_years = st.slider(
    "For how many years are you planning your life goals?",
    5, 30, 10
)

st.markdown("---")

# ================= INCOME & EXPENSES =================
st.subheader("2️⃣ Income and unavoidable expenses")

salary = st.number_input(
    "Monthly income (₹)",
    min_value=0,
    step=5000
)

expenses = st.number_input(
    "Monthly unavoidable expenses (₹)",
    min_value=0,
    step=2000
)

if salary <= 0:
    st.warning("Please enter income to continue.")
    st.stop()

if expenses >= salary:
    st.error("Expenses exceed income. No surplus is available.")
    st.stop()

base_surplus = salary - expenses
st.success(f"Base monthly surplus: ₹{base_surplus:,.0f}")

st.markdown("---")

# ================= LIFE CONSTRAINTS =================
st.subheader("3️⃣ Life conditions")

job = st.selectbox(
    "Job stability",
    [
        "Stable income (0% penalty)",
        "Somewhat unstable income (5% penalty)",
        "Highly unstable income (12% penalty)"
    ]
)

health = st.selectbox(
    "Health and exercise routine",
    [
        "Good routine (0% penalty)",
        "Irregular routine (5% penalty)",
        "Poor routine (10% penalty)"
    ]
)

work = st.selectbox(
    "Work pattern",
    [
        "Balanced and sustainable (0% penalty)",
        "Aggressive long hours (8% income boost)",
        "Frequent burnout cycles (12% penalty)"
    ]
)

family = st.selectbox(
    "Living arrangement",
    [
        "Living with family (5% lower expenses)",
        "Living away from family (5% higher expenses)"
    ]
)

# ================= PENALTY CALCULATION =================
income_penalty = 0.0
expense_penalty = 0.0

if "5%" in job:
    income_penalty += 0.05
elif "12%" in job:
    income_penalty += 0.12

if "5%" in health:
    income_penalty += 0.05
elif "10%" in health:
    income_penalty += 0.10

if "Aggressive" in work:
    income_penalty -= 0.08
elif "12%" in work:
    income_penalty += 0.12

if "with family" in family:
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

adjusted_income = salary * (1 - income_penalty)
adjusted_expenses = expenses * (1 + expense_penalty)
adjusted_surplus = adjusted_income - adjusted_expenses

st.markdown("### Effect of life conditions")
st.write(f"Income impact: {income_penalty*100:.1f}%")
st.write(f"Expense impact: {expense_penalty*100:.1f}%")
st.info(f"Usable monthly surplus: ₹{adjusted_surplus:,.0f}")

if adjusted_surplus <= 0:
    st.error("After applying constraints, no usable surplus remains.")
    st.stop()

st.markdown("---")

# ================= FEASIBLE CAPACITY =================
st.subheader("4️⃣ Feasible capacity")

feasible_capacity = adjusted_surplus * 12 * horizon_years
st.success(f"Total money available over {horizon_years} years: ₹{feasible_capacity:,.0f}")

st.markdown("---")

# ================= GOALS =================
st.subheader("5️⃣ Life goals")

goals = {}
goals["Asset creation"] = st.number_input("Asset creation (₹)", 0, step=100000)
goals["Emergency fund"] = st.number_input("Emergency fund (₹)", 0, step=50000)
goals["Education / loan repayment"] = st.number_input("Education / loan repayment (₹)", 0, step=50000)
goals["Marriage & family"] = st.number_input("Marriage & family (₹)", 0, step=50000)
goals["Social contribution"] = st.number_input("Social contribution (₹)", 0, step=20000)

total_goal_amount = sum(goals.values())

st.markdown("---")

# ================= IMPORTANCE =================
st.subheader("6️⃣ Importance of goals")

importance = {}
for g in goals:
    importance[g] = st.slider(f"Importance of {g}", 1, 10, 5)

st.markdown("---")

# ================= CHECK FEASIBILITY =================
st.subheader("7️⃣ Feasibility check")

if feasible_capacity >= total_goal_amount:

    st.success("🎉 All goals are achievable under your current assumptions.")

    st.markdown("### Monthly saving plan")
    for g in goals:
        st.write(
            f"Save **₹{goals[g] / (horizon_years * 12):,.0f} per month** for {g}"
        )

else:

    st.warning("⚠️ All goals are not achievable together. An optimized plan is suggested.")

    # ================= OPTIMIZATION =================
    MIN_PERCENT = 0.35
    optimized = {}
    remaining = feasible_capacity

    for g in goals:
        optimized[g] = min(goals[g] * MIN_PERCENT, remaining)
        remaining -= optimized[g]

    for g in sorted(goals, key=lambda x: importance[x], reverse=True):
        if remaining <= 0:
            break
        extra = min(goals[g] - optimized[g], remaining)
        optimized[g] += extra
        remaining -= extra

    # ================= RESULTS TABLE =================
    result_rows = []
    for g in goals:
        achieved_pct = (optimized[g] / goals[g] * 100) if goals[g] > 0 else 0
        result_rows.append([
            g,
            f"₹{goals[g]:,.0f}",
            f"₹{optimized[g]:,.0f}",
            f"{achieved_pct:.1f}%"
        ])

    st.dataframe(
        pd.DataFrame(
            result_rows,
            columns=[
                "Goal",
                "Target (₹)",
                "Allocated (₹)",
                "Fulfilment (%)"
            ]
        ),
        use_container_width=True
    )

    st.markdown("### Monthly saving plan (optimized)")
    for g in optimized:
        st.write(
            f"Save **₹{optimized[g] / (horizon_years * 12):,.0f} per month** for {g}"
        )

# ================= SAVE RESPONSES =================
st.markdown("---")
st.subheader("📥 Classroom response capture")

consent = st.checkbox("I allow my anonymous response to be saved for academic analysis")

if consent:
    record = {
        "timestamp": datetime.now(),
        "salary": salary,
        "expenses": expenses,
        "planning_years": horizon_years,
        "total_goals": total_goal_amount,
        "feasible_capacity": feasible_capacity
    }

    df = pd.DataFrame([record])
    df.to_csv(
        "responses.csv",
        mode="a",
        header=not os.path.exists("responses.csv"),
        index=False
    )

    st.success("Response saved successfully.")
