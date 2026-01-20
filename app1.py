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
st.subheader("2️⃣ Income & unavoidable expenses")

salary = st.number_input("Current monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Monthly unavoidable expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.warning("Please enter your income to continue.")
    st.stop()

base_surplus = salary - expenses

# ================= LIFE CONDITIONS (SIMPLE QUESTIONS) =================
st.subheader("3️⃣ Your current life conditions")

job = st.selectbox("Job stability", ["Stable", "Somewhat unstable", "Highly unstable"])
health = st.selectbox("Health routine", ["Good", "Irregular", "Poor"])
family = st.selectbox("Living arrangement", ["With family", "Away from family"])
work = st.selectbox("Work style", ["Balanced", "Aggressive long hours", "Frequent burnout"])

# ================= APPLY LIFE EFFECTS =================
income_penalty = 0
expense_penalty = 0

if job == "Somewhat unstable":
    income_penalty += 0.05
elif job == "Highly unstable":
    income_penalty += 0.12

if health == "Irregular":
    income_penalty += 0.05
elif health == "Poor":
    income_penalty += 0.10

if family == "With family":
    expense_penalty -= 0.05
else:
    expense_penalty += 0.05

if work == "Aggressive long hours":
    income_penalty -= 0.08
elif work == "Frequent burnout":
    income_penalty += 0.12

adjusted_surplus = base_surplus * (1 - income_penalty) * (1 - expense_penalty)

st.info(f"Usable monthly surplus after life effects: ₹{adjusted_surplus:,.0f}")

# ================= INFLATION-ADJUSTED CAPACITY =================
inflation_rate = 0.04
current_salary = salary
yearly_surplus = []

for year in range(horizon_years):
    annual_surplus = (current_salary - expenses) * 12
    yearly_surplus.append(max(annual_surplus, 0))
    current_salary *= (1 + inflation_rate)

feasible_capacity = sum(yearly_surplus)

# ================= GOALS =================
st.subheader("4️⃣ Life goals (total amount needed)")

goals = {
    "Asset creation": st.number_input("House / land / vehicle (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education / loan repayment (₹)", 0, step=50000),
    "Marriage & family setup": st.number_input("Marriage & family setup (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution (₹)", 0, step=20000),
}

# ================= IMPORTANCE =================
st.subheader("5️⃣ If this goal is delayed, how uncomfortable would you feel?")

importance = {}
for g in goals:
    importance[g] = st.slider(g, 10, 100, 50)

# ================= DEVIATION DIAGNOSIS =================
if st.button("1️⃣ Show deviation diagnosis"):

    avg_allocation = feasible_capacity / len(goals)
    deviation = {g: goals[g] - avg_allocation for g in goals}
    max_dev_goal = max(deviation, key=lambda x: abs(deviation[x]))

    st.session_state.update({
        "avg": avg_allocation,
        "deviation": deviation,
        "capacity": feasible_capacity
    })

    fig, ax = plt.subplots()
    ax.bar(deviation.keys(), deviation.values())
    ax.axhline(0)
    ax.set_title("Deviation from Average Allocation")
    plt.xticks(rotation=30)
    st.pyplot(fig)

    st.info(f"Maximum deviation is observed in: **{max_dev_goal}**")

# ================= PDF FUNCTION =================
def generate_pdf(data, goals, monthly_plan):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("IRMAN'S DREAM CALCULATOR – OPTIMIZED PLAN", styles["Title"]))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"Planning horizon: {data['years']} years", styles["Normal"]))
    elements.append(Paragraph(f"Feasible capacity: ₹{data['capacity']:,.0f}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    table_data = [["Goal", "Monthly saving required (₹)"]]
    for g in monthly_plan:
        table_data.append([g, f"{monthly_plan[g]:,.0f}"])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "Action steps:<br/>"
        "1. Automate monthly savings.<br/>"
        "2. Avoid lifestyle inflation.<br/>"
        "3. Revisit plan annually or after major life changes.",
        styles["Normal"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================= OPTIMIZATION =================
if st.button("2️⃣ Optimize my plan"):

    st.audio("success.mp3", autoplay=True)

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

    st.subheader("📅 Your monthly action plan")
    for g in monthly_plan:
        st.write(f"Save ₹{monthly_plan[g]:,.0f} per month for **{g}**")

    if feasible_capacity >= sum(goals.values()):
        extra = (feasible_capacity - sum(goals.values())) / (horizon_years * 12)
        st.success(
            f"All goals are achievable within {horizon_years} years. "
            f"You will still have a monthly surplus of ₹{extra:,.0f}."
        )

    consent = st.checkbox(
        "I allow my anonymous data to be used for academic research"
    )

    pdf = generate_pdf(
        {"years": horizon_years, "capacity": feasible_capacity},
        goals,
        monthly_plan
    )

    st.download_button(
        "📄 Download optimized life plan (PDF)",
        pdf,
        file_name="optimized_life_plan.pdf",
        mime="application/pdf"
    )

    if consent:
        record = {
            "timestamp": datetime.now(),
            "capacity": feasible_capacity
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
        "This tool does not tell you what to do — it helps you see clearly and decide confidently."
    )
