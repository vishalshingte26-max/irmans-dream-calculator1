import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================================================
# IRMAN'S DREAM CALCULATOR
# Constraint-Based Life Planning Model
#
# IMPORTANT FOR STUDENTS:
# This code treats life planning as a RESOURCE ALLOCATION problem.
# Income is LIMITED.
# Goals are MANY.
# Lifestyle choices tighten or relax constraints.
# =========================================================

st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")
st.title("IRMAN'S DREAM CALCULATOR")

st.markdown(
    """
This tool shows **how life goals compete for limited money**.

Read the comments in the code to understand:
- how surplus is calculated
- how constraints are applied
- how optimisation redistributes money
"""
)

# =========================================================
# 1. PLANNING HORIZON
# =========================================================
# Time horizon fixes the TIME over which money can be accumulated
# All long-term goals are planned within this window

horizon_years = st.slider(
    "For how many years are you planning your life goals?",
    5, 30, 10
)

# =========================================================
# 2. INCOME AND EXPENSES
# =========================================================
# These are HARD INPUTS.
# If expenses exceed income, planning is infeasible.

salary = st.number_input("Monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Monthly unavoidable expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.stop()

if expenses >= salary:
    st.error("Expenses exceed income. No planning possible.")
    st.stop()

# Base surplus is the starting flexibility BEFORE life conditions
base_surplus = salary - expenses
st.success(f"Base monthly surplus: ₹{base_surplus:,.0f}")

# =========================================================
# 3. LIFE CONDITIONS → CONSTRAINT ADJUSTMENTS
# =========================================================
# These questions DO NOT change goals.
# They MODIFY income and expenses, i.e., CONSTRAINTS.

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

# ---------------------------------------------------------
# Compute income and expense penalties
# ---------------------------------------------------------
income_penalty = 0.0
expense_penalty = 0.0

# Income penalties reduce EFFECTIVE income
if "5%" in job:
    income_penalty += 0.05
elif "12%" in job:
    income_penalty += 0.12

if "5%" in health:
    income_penalty += 0.05
elif "10%" in health:
    income_penalty += 0.10

# Aggressive work boosts income, burnout reduces it
if "Aggressive" in work:
    income_penalty -= 0.08
elif "12%" in work:
    income_penalty += 0.12

# Living with family reduces expenses, living away increases them
if "with family" in family:
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

# ---------------------------------------------------------
# Adjust income and expenses using penalties
# ---------------------------------------------------------
adjusted_income = salary * (1 - income_penalty)
adjusted_expenses = expenses * (1 + expense_penalty)

# REAL usable surplus after applying life constraints
adjusted_surplus = adjusted_income - adjusted_expenses

st.info(f"Usable monthly surplus after life conditions: ₹{adjusted_surplus:,.0f}")

if adjusted_surplus <= 0:
    st.error("After constraints, no usable surplus remains.")
    st.stop()

# =========================================================
# 4. FEASIBLE CAPACITY (HARD CONSTRAINT)
# =========================================================
# Salary growth ≈ inflation → real growth ≈ 0
# So surplus is assumed constant in real terms

feasible_capacity = adjusted_surplus * 12 * horizon_years
st.success(f"Total money available over {horizon_years} years: ₹{feasible_capacity:,.0f}")

# =========================================================
# 5. LIFE GOALS (SOFT CONSTRAINTS)
# =========================================================
# Goals are TARGETS, not decisions.
# The model decides how much can be allocated to each.

goals = {
    "Asset creation": st.number_input("Asset creation (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education / loan repayment (₹)", 0, step=50000),
    "Marriage & family": st.number_input("Marriage & family (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution (₹)", 0, step=20000),
}

total_goals = sum(goals.values())

# =========================================================
# 6. IMPORTANCE WEIGHTS
# =========================================================
# Importance = how painful it is if a goal is NOT achieved
# These weights guide where compromise should happen

importance = {}
for g in goals:
    importance[g] = st.slider(f"Importance of {g}", 1, 10, 5)

# =========================================================
# 7. FEASIBILITY CHECK
# =========================================================
# If total goals fit within feasible capacity,
# NO optimisation is needed.

if feasible_capacity >= total_goals:

    st.success("All goals are achievable under current constraints.")

    for g in goals:
        st.write(
            f"Save ₹{goals[g] / (horizon_years * 12):,.0f} per month for {g}"
        )

else:
    st.warning("All goals cannot be achieved together. Optimisation is required.")

    # =====================================================
    # 8. OPTIMISATION LOGIC (THIS IS THE CORE)
    # =====================================================
    # STEP 1: Guarantee minimum progress to EVERY goal
    # This avoids completely ignoring any goal
    MIN_PERCENT = 0.35

    optimized = {}
    remaining_money = feasible_capacity

    # Allocate minimum guaranteed amount first
    for g in goals:
        optimized[g] = min(goals[g] * MIN_PERCENT, remaining_money)
        remaining_money -= optimized[g]

    # STEP 2: Allocate remaining money based on importance
    # More important goals get priority
    for g in sorted(goals, key=lambda x: importance[x], reverse=True):
        if remaining_money <= 0:
            break
        extra = min(goals[g] - optimized[g], remaining_money)
        optimized[g] += extra
        remaining_money -= extra

    # =====================================================
    # 9. DISPLAY RESULTS
    # =====================================================
    rows = []
    for g in goals:
        rows.append([
            g,
            f"₹{goals[g]:,.0f}",
            f"₹{optimized[g]:,.0f}",
            f"{(optimized[g] / goals[g] * 100) if goals[g] > 0 else 0:.1f}%"
        ])

    st.dataframe(
        pd.DataFrame(
            rows,
            columns=["Goal", "Target", "Allocated", "Fulfilment (%)"]
        ),
        use_container_width=True
    )

    st.markdown("### Monthly saving plan (optimised)")
    for g in optimized:
        st.write(
            f"Save ₹{optimized[g] / (horizon_years * 12):,.0f} per month for {g}"
        )
# ================= SAVE CLASSROOM RESPONSES (DETAILED) =================

consent = st.checkbox("I allow my anonymous response to be saved for academic analysis")

if consent:

    # Decide whether optimisation was required
    optimisation_status = "Not required (all goals achievable)" if feasible_capacity >= total_goals else "Required"

    # Create base record
    record = {
        "timestamp": datetime.now(),
        "monthly_income": salary,
        "monthly_expenses": expenses,
        "planning_years": horizon_years,
        "total_goal_amount": total_goals,
        "feasible_capacity": feasible_capacity,
        "optimisation_status": optimisation_status
    }

    # Decide which allocation to save
    # If all goals are achievable → allocated = target
    # If not → allocated = optimized value
    allocation_source = goals if feasible_capacity >= total_goals else optimized

    # Store goal-wise details
    for g in goals:
        allocated_amount = allocation_source[g]
        target_amount = goals[g]
        achievement_pct = (allocated_amount / target_amount * 100) if target_amount > 0 else 0

        record[f"{g}_target"] = target_amount
        record[f"{g}_allocated"] = allocated_amount
        record[f"{g}_achievement_pct"] = round(achievement_pct, 1)

    # Save to CSV
    df = pd.DataFrame([record])

    df.to_csv(
        "responses.csv",
        mode="a",
        header=not os.path.exists("responses.csv"),
        index=False
    )

    st.success("Your response has been saved successfully.")
