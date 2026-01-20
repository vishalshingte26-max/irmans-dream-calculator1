import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

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

base_surplus = salary - expenses

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

# ================= APPLY EFFECTS =================
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

adjusted_surplus = base_surplus * (1 - income_penalty) * (1 - expense_penalty)

st.info(f"Usable monthly surplus after life effects: ₹{adjusted_surplus:,.0f}")

# ================= SALARY GROWTH =================
st.subheader("4️⃣ Income growth assumption")
st.markdown("Salary is assumed to grow at **4% per year**, roughly matching inflation.")

inflation_rate = 0.04
current_salary = salary
yearly_surplus = []

for _ in range(horizon_years):
    annual_surplus = (current_salary - expenses) * 12
    yearly_surplus.append(max(annual_surplus, 0))
    current_salary *= (1 + inflation_rate)

feasible_capacity = sum(yearly_surplus)

st.success(f"Total money available over {horizon_years} years: ₹{feasible_capacity:,.0f}")

# ================= GOALS =================
st.subheader("5️⃣ Life goals (total amount required)")

goals = {
    "Asset creation": st.number_input("House / land / vehicle (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education / loan repayment (₹)", 0, step=50000),
    "Marriage & family setup": st.number_input("Marriage & family setup (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution (₹)", 0, step=20000),
}

# ================= IMPORTANCE =================
st.subheader("6️⃣ If this goal is delayed, how uncomfortable would you feel?")
importance = {g: st.slider(g, 10, 100, 50) for g in goals}

# ================= WITHOUT OPTIMIZATION GRAPH =================
if st.button("1️⃣ Show deviation (without optimization)"):

    avg_allocation = feasible_capacity / len(goals)
    deviation = {g: goals[g] - avg_allocation for g in goals}

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(goals.keys(), goals.values())
    ax.axhline(avg_allocation)

    ax.text(
        0.5, avg_allocation,
        f"Average available per goal = ₹{avg_allocation:,.0f}",
        transform=ax.get_yaxis_transform(),
        fontsize=10,
        verticalalignment="bottom"
    )

    ax.set_ylabel("Money required (₹)")
    ax.set_title("Goal requirements vs average available money (No optimization)")
    plt.xticks(rotation=30)

    for bar, g in zip(bars, goals.keys()):
        gap = deviation[g]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{gap:+,.0f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    st.pyplot(fig)

    st.markdown(
        """
        **Interpretation:**
        - Bars show full money required for each goal (₹)
        - Horizontal line shows average money available per goal (₹)
        - Numbers on bars show surplus (+₹) or shortfall (−₹)
        - This mismatch exists because total money is limited
        """
    )

# ================= OPTIMIZATION =================
if st.button("2️⃣ Optimize my plan"):

    MIN_PERCENT = 0.35
    optimized = {}
    remaining = feasible_capacity

    for g in goals:
        alloc = min(goals[g] * MIN_PERCENT, remaining)
        optimized[g] = alloc
        remaining -= alloc

    for g in sorted(goals, key=lambda x: importance[x], reverse=True):
        if remaining <= 0:
            break
        extra = min(goals[g] - optimized[g], remaining)
        optimized[g] += extra
        remaining -= extra

    # ===== VISUALLY APPEALING STACKED BAR =====
    st.subheader("📊 Optimal allocation under income constraint")

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bottom = 0

    for g in optimized:
        ax2.bar("Total Available Money", optimized[g], bottom=bottom, label=g)
        bottom += optimized[g]

    ax2.set_ylabel("Money allocated (₹)")
    ax2.set_title("How total money is optimally distributed across goals")
    ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    st.pyplot(fig2)

    st.markdown(
        f"""
        **Constraint:** Total available money = ₹{feasible_capacity:,.0f}

        **Optimization logic:**
        - Every goal receives a minimum guaranteed allocation
        - Remaining money is allocated based on importance (weightage)
        - This allocation maximizes overall goal achievement under the constraint
        """
    )

    # ===== MONTHLY PLAN =====
    st.subheader("📅 Monthly saving plan")

    for g in optimized:
        monthly = optimized[g] / (horizon_years * 12)
        st.write(f"Save **₹{monthly:,.0f} per month** for {g}")

    st.success(
        "Given your income constraint, this is the optimal allocation to achieve maximum possible goals."
    )

    st.markdown("---")
    st.markdown(
        "**Thank you for using IRMAN’S Dream Calculator.**  \n"
        "This plan shows what is realistically achievable and how to act on it."
    )
