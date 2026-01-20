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
    "**A practical life-planning tool that shows how close your income path is to your goals — and how small changes can make it optimal.**"
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
    st.warning("Please enter your income to continue.")
    st.stop()

base_surplus = salary - expenses

# ================= LIFE CONDITIONS (WITH % IMPACT SHOWN) =================
st.subheader("3️⃣ Your current life conditions (with impact shown clearly)")

job = st.selectbox(
    "Job stability (impact on income)",
    [
        "Stable (0% change)",
        "Somewhat unstable (−5% income)",
        "Highly unstable (−12% income)"
    ]
)

health = st.selectbox(
    "Health routine (impact on income)",
    [
        "Good routine (0% change)",
        "Irregular routine (−5% income)",
        "Poor health habits (−10% income)"
    ]
)

family = st.selectbox(
    "Living arrangement (impact on expenses)",
    [
        "Living with family (−5% expenses)",
        "Living away from family (+5% expenses)"
    ]
)

work = st.selectbox(
    "Work style (impact on income)",
    [
        "Balanced & sustainable (0% change)",
        "Aggressive long hours (+8% income)",
        "Frequent burnout cycles (−12% income)"
    ]
)

# ================= APPLY LIFE EFFECTS =================
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

if "−5% expenses" in family:
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

if "+8%" in work:
    income_penalty -= 0.08
elif "−12%" in work:
    income_penalty += 0.12

adjusted_surplus = base_surplus * (1 - income_penalty) * (1 - expense_penalty)

st.info(
    f"After considering life conditions, usable monthly surplus becomes **₹{adjusted_surplus:,.0f}**"
)

# ================= SALARY GROWTH WITH INFLATION =================
st.subheader("4️⃣ Income growth assumption")

st.markdown(
    "We assume your **salary grows at 4% per year**, roughly matching long-term inflation."
)

inflation_rate = 0.04
current_salary = salary
yearly_surplus = []

for year in range(1, horizon_years + 1):
    annual_surplus = (current_salary - expenses) * 12
    yearly_surplus.append(max(annual_surplus, 0))
    current_salary *= (1 + inflation_rate)

feasible_capacity = sum(yearly_surplus)

st.success(f"Total money realistically available over {horizon_years} years: ₹{feasible_capacity:,.0f}")

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
    importance[g] = st.slider(
        g,
        10,
        100,
        50,
        help="Higher value means you mentally struggle more if this goal is delayed"
    )

# ================= DEVIATION DIAGNOSIS =================
if st.button("1️⃣ Show deviation diagnosis"):

    avg_allocation = feasible_capacity / len(goals)

    deviation = {}
    for g in goals:
        deviation[g] = goals[g] - avg_allocation

    max_dev_goal = max(deviation, key=lambda x: abs(deviation[x]))

    st.session_state["capacity"] = feasible_capacity
    st.session_state["deviation"] = deviation

    fig, ax = plt.subplots()
    ax.bar(deviation.keys(), deviation.values())
    ax.axhline(0)
    ax.set_ylabel("Deviation from average allocation (₹)")
    ax.set_title("Where your money demand deviates from an average plan")
    plt.xticks(rotation=30)
    st.pyplot(fig)

    st.markdown("### What this graph means:")
    st.write(
        "• Bars **above zero** → this goal needs **more money than average**\n"
        "• Bars **below zero** → this goal needs **less money than average**\n"
        "• Taller bars → **bigger pressure on your income**"
    )

    st.info(f"Maximum financial pressure is coming from **{max_dev_goal}**")

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

    st.subheader("📅 Your practical monthly saving plan")

    for g in monthly_plan:
        st.write(f"Save **₹{monthly_plan[g]:,.0f} per month** for {g}")

    if feasible_capacity >= sum(goals.values()):
        extra = (feasible_capacity - sum(goals.values())) / (horizon_years * 12)
        st.success(
            f"All goals are achievable within {horizon_years} years. "
            f"You will still have a surplus of **₹{extra:,.0f} per month**."
        )

    consent = st.checkbox(
        "I allow my anonymous data to be used for academic research"
    )

    if consent:
        record = {
            "timestamp": datetime.now(),
            "feasible_capacity": feasible_capacity
        }
        df = pd.DataFrame([record])
        if not os.path.exists("responses.csv"):
            df.to_csv("responses.csv", index=False)
        else:
            df.to_csv("responses.csv", mode="a", header=False, index=False)

        st.success("Thank you. Your data has been saved anonymously.")

    st.markdown("---")
    st.markdown(
        "**Thank you for using IRMAN’S Dream Calculator.**  \n"
        "This tool does not force decisions — it helps you understand trade-offs clearly."
    )
