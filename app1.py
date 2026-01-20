import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

# ================= PAGE CONFIG =================
st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

st.title("IRMAN'S DREAM CALCULATOR")
st.markdown(
    "**A practical life-planning tool that shows how limited income can be optimally allocated to achieve maximum life goals.**"
)

st.markdown("---")

# ================= PLANNING HORIZON =================
st.subheader("1️⃣ Planning horizon")
horizon_years = st.slider("How many years do you want to plan for?", 5, 30, 10)

# ================= INCOME =================
st.subheader("2️⃣ Current income & unavoidable expenses")

salary = st.number_input("Current monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Monthly unavoidable expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.warning("Please enter income to continue.")
    st.stop()

# ================= LIFE CONDITIONS =================
st.subheader("3️⃣ Life conditions (impact shown clearly)")

job = st.selectbox(
    "Job stability (impact on income)",
    ["Stable (0%)", "Somewhat unstable (−5%)", "Highly unstable (−12%)"]
)

health = st.selectbox(
    "Health routine (impact on income)",
    ["Good routine (0%)", "Irregular routine (−5%)", "Poor health habits (−10%)"]
)

family = st.selectbox(
    "Living arrangement (impact on expenses)",
    ["Living with family (−5%)", "Living away from family (+5%)"]
)

work = st.selectbox(
    "Work style (impact on income)",
    ["Balanced & sustainable (0%)", "Aggressive long hours (+8%)", "Frequent burnout cycles (−12%)"]
)

income_penalty = 0
expense_penalty = 0

if "−5%" in job:
    income_penalty += 0.05
elif "−12%" in job:
    income_penalty += 0.12

if "−5%" in health:
    income_penalty += 0.05
elif "−10%" in health:
    income_penalty += 0.10

if "−5%" in family:
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

if "+8%" in work:
    income_penalty -= 0.08
elif "−12%" in work:
    income_penalty += 0.12

base_surplus = salary - expenses
adjusted_surplus = base_surplus * (1 - income_penalty) * (1 - expense_penalty)

st.info(f"Usable monthly surplus after life effects: ₹{adjusted_surplus:,.0f}")

# ================= SALARY GROWTH =================
st.subheader("4️⃣ Income growth assumption")
st.markdown("Salary grows at **4% per year**, approximately matching inflation.")

inflation_rate = 0.04
current_salary = salary
yearly_surplus = []

for _ in range(horizon_years):
    yearly_surplus.append(max((current_salary - expenses) * 12, 0))
    current_salary *= (1 + inflation_rate)

feasible_capacity = sum(yearly_surplus)

st.success(f"Total money available over {horizon_years} years: ₹{feasible_capacity:,.0f}")

# ================= GOALS =================
st.subheader("5️⃣ Life goals")

goals = {
    "Asset creation": st.number_input("House / land / vehicle (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education / loan repayment (₹)", 0, step=50000),
    "Marriage & family setup": st.number_input("Marriage & family setup (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution (₹)", 0, step=20000),
}

importance = {g: st.slider(f"Importance of {g}", 10, 100, 50) for g in goals}

# ================= BEFORE OPTIMIZATION =================
avg_allocation = feasible_capacity / len(goals)
before_alloc = {g: min(goals[g], avg_allocation) for g in goals}

st.subheader("📌 Before optimization: constraint reality")

before_rows = []
for g in goals:
    before_rows.append([
        g,
        f"₹{goals[g]:,.0f}",
        f"₹{avg_allocation:,.0f}",
        f"₹{goals[g] - avg_allocation:,.0f}"
    ])

st.dataframe(
    pd.DataFrame(
        before_rows,
        columns=[
            "Goal",
            "Goal amount (₹)",
            "Average available per goal (₹)",
            "Gap (+need / −excess) (₹)"
        ]
    ),
    use_container_width=True
)

# ================= OPTIMIZATION =================
if st.button("2️⃣ Optimize my plan"):

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

    # ================= BEFORE vs AFTER TABLE =================
    st.subheader("📊 Goal achievement: before vs after optimization")

    compare_rows = []
    for g in goals:
        before_pct = (before_alloc[g] / goals[g] * 100) if goals[g] > 0 else 0
        after_pct = (optimized[g] / goals[g] * 100) if goals[g] > 0 else 0

        compare_rows.append([
            g,
            f"₹{before_alloc[g]:,.0f}",
            f"{before_pct:.1f}%",
            f"₹{optimized[g]:,.0f}",
            f"{after_pct:.1f}%"
        ])

    st.dataframe(
        pd.DataFrame(
            compare_rows,
            columns=[
                "Goal",
                "Achieved before (₹)",
                "Achieved before (%)",
                "Achieved after (₹)",
                "Achieved after (%)"
            ]
        ),
        use_container_width=True
    )

    # ================= OPTIMIZATION GRAPH (₹ SHOWN ON BAR) =================
    st.subheader("📊 Optimal allocation under income constraint")

    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = 0

    for g in optimized:
        ax.bar("Total Available Money", optimized[g], bottom=bottom)
        ax.text(
            0,
            bottom + optimized[g] / 2,
            f"{g}\n₹{optimized[g]:,.0f}",
            ha="center",
            va="center",
            fontsize=9
        )
        bottom += optimized[g]

    ax.set_ylabel("Money allocated (₹)")
    ax.set_title("How total available money is optimally allocated")

    st.pyplot(fig)

    # ================= MONTHLY PLAN =================
    st.subheader("📅 Monthly saving plan")

    for g in optimized:
        st.write(f"Save **₹{optimized[g] / (horizon_years * 12):,.0f} per month** for {g}")

    # ================= SAVE RESPONDENT DATA =================
    consent = st.checkbox("I allow my anonymous data to be saved for academic research")

    if consent:
        record = {
            "timestamp": datetime.now(),
            "salary": salary,
            "expenses": expenses,
            "years": horizon_years,
            "feasible_capacity": feasible_capacity
        }

        df = pd.DataFrame([record])
        df.to_csv(
            "responses.csv",
            mode="a",
            header=not os.path.exists("responses.csv"),
            index=False
        )

        st.success("Your response has been saved anonymously.")

    st.success(
        "Given the income constraint, this allocation maximizes overall goal achievement based on your priorities."
    )
