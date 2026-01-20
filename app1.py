import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import io
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ================= PAGE CONFIG =================
st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

st.title("IRMAN'S DREAM CALCULATOR")
st.markdown(
    "**A practical life-planning tool that shows how your limited income can be optimally allocated to achieve maximum life goals.**"
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

# ================= LIFE CONDITIONS WITH % =================
st.subheader("3️⃣ Life conditions (impact shown clearly)")

job = st.selectbox(
    "Job stability (impact on income)",
    [
        "Stable (0%)",
        "Somewhat unstable (−5%)",
        "Highly unstable (−12%)"
    ]
)

health = st.selectbox(
    "Health routine (impact on income)",
    [
        "Good routine (0%)",
        "Irregular routine (−5%)",
        "Poor health habits (−10%)"
    ]
)

family = st.selectbox(
    "Living arrangement (impact on expenses)",
    [
        "Living with family (−5%)",
        "Living away from family (+5%)"
    ]
)

work = st.selectbox(
    "Work style (impact on income)",
    [
        "Balanced & sustainable (0%)",
        "Aggressive long hours (+8%)",
        "Frequent burnout cycles (−12%)"
    ]
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

st.markdown("We assume **salary grows at 4% per year**, approximately matching inflation.")

inflation_rate = 0.04
current_salary = salary
yearly_surplus = []

for year in range(1, horizon_years + 1):
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

importance = {}
for g in goals:
    importance[g] = st.slider(g, 10, 100, 50)

# ================= DEVIATION GRAPH =================
if st.button("1️⃣ Show deviation diagnosis"):

    avg_allocation = feasible_capacity / len(goals)
    deviation = {g: goals[g] - avg_allocation for g in goals}
    max_dev_goal = max(deviation, key=lambda x: abs(deviation[x]))

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(goals.keys(), goals.values())
    ax.axhline(avg_allocation)  # SOLID LINE (NO DASHES)

    ax.set_ylabel("Money required (₹)")
    ax.set_title("Goal requirements vs average available money")
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

    st.markdown("### How to read this graph")
    st.write(
        f"""
        • The **horizontal line** shows average money available per goal  
          (₹{avg_allocation:,.0f})

        • Bars show actual money required for each goal

        • Numbers on bars show **extra (+₹)** or **shortfall (−₹)** from the average

        • This happens because total money is **limited**
        """
    )

    st.info(
        f"Maximum pressure comes from **{max_dev_goal}**, "
        f"which needs ₹{abs(deviation[max_dev_goal]):,.0f} more than average."
    )

    st.markdown(
        """
        **Constraint:**  
        Your total money over time is fixed by income and expenses.

        **Next step:**  
        Optimization will redistribute this fixed money using your priorities,
        so maximum goals can be achieved.
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

    monthly_plan = {g: optimized[g] / (horizon_years * 12) for g in goals}

    st.subheader("📊 Optimal allocation of your total money")

    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie(
        optimized.values(),
        labels=optimized.keys(),
        autopct=lambda p: f"{p:.1f}%\n₹{p/100*sum(optimized.values()):,.0f}",
        startangle=90
    )
    ax_pie.axis("equal")
    st.pyplot(fig_pie)

    st.markdown(
        """
        This pie shows **how your limited money is distributed optimally**
        based on importance and constraints.
        """
    )

    st.subheader("📅 Monthly saving plan")

    for g in monthly_plan:
        st.write(f"Save **₹{monthly_plan[g]:,.0f} per month** for {g}")

    st.success(
        "Given your income constraint, this is the optimal allocation that maximizes goal achievement based on your priorities."
    )

    st.markdown("---")
    st.markdown(
        "**Thank you for using IRMAN’S Dream Calculator.**  \n"
        "This plan shows what is realistically achievable — and how to move towards it optimally."
    )
