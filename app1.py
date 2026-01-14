import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ================= PAGE CONFIG =================
st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

st.title("IRMAN'S DREAM CALCULATOR")

st.markdown("""
A life planning tool that shows **where stress comes from**  
and **how optimization can reduce it**.

The model does not force decisions.  
It only shows trade-offs clearly.
""")

st.markdown("---")

# ================= TIME HORIZON =================
st.subheader("1️⃣ Planning horizon")
st.caption("More years reduce pressure. Fewer years increase stress.")

horizon_years = st.slider("For how many years are you planning your life goals?", 5, 30, 10)

# ================= INCOME =================
st.subheader("2️⃣ Income and unavoidable expenses")

salary = st.number_input("Monthly income (₹)", min_value=0, step=5000)
expenses = st.number_input("Monthly unavoidable expenses (₹)", min_value=0, step=2000)

if salary <= 0:
    st.warning("Income is required")
    st.stop()

base_surplus = salary - expenses
if base_surplus <= 0:
    st.error("Expenses exceed income. No surplus available.")
    st.stop()

st.success(f"Monthly money available for goals: ₹{base_surplus:,.0f}")

# ================= LIFE CONDITIONS =================
st.subheader("3️⃣ Life conditions (explained clearly)")

job = st.selectbox(
    "Job stability",
    [
        "Stable and satisfying (no penalty)",
        "Somewhat unstable (5% income loss)",
        "Highly unstable or stressful (12% income loss)"
    ]
)
st.caption("Unstable jobs reduce savings due to uncertainty and switching costs.")

health = st.selectbox(
    "Health routine",
    [
        "Good sleep and exercise (no penalty)",
        "Irregular routine (5% income loss)",
        "Poor health habits (10% income loss)"
    ]
)
st.caption("Poor health increases medical costs and reduces productivity.")

aqi = st.selectbox(
    "Air quality",
    [
        "Mostly good AQI (no penalty)",
        "Moderate AQI (4% expense increase)",
        "Poor AQI most of the year (8% expense increase)"
    ]
)
st.caption("Poor air quality leads to higher health-related expenses.")

family = st.selectbox(
    "Living arrangement",
    [
        "Living with family (5% lower expenses)",
        "Living away from family (5% higher expenses)"
    ]
)
st.caption("Living alone usually increases rent, food, and support costs.")

work = st.selectbox(
    "Work style",
    [
        "Balanced and sustainable (no penalty)",
        "Aggressive long hours (8% income boost)",
        "Frequent burnout cycles (12% income loss)"
    ]
)
st.caption("Burnout reduces long-term earning capacity.")

# ================= APPLY PENALTIES =================
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

# ================= GOALS =================
st.subheader("4️⃣ Life goals")

goals = {
    "Asset creation": st.number_input("House / land / vehicle (₹)", 0, step=100000),
    "Emergency fund": st.number_input("Emergency fund (₹)", 0, step=50000),
    "Education / loan repayment": st.number_input("Education or loan repayment (₹)", 0, step=50000),
    "Marriage & family setup": st.number_input("Marriage & family setup (₹)", 0, step=50000),
    "Social contribution": st.number_input("Social contribution (₹)", 0, step=20000),
}

# ================= IMPORTANCE =================
st.subheader("5️⃣ Importance of each goal (%)")
st.caption("Higher % means more stress if this goal is delayed")

importance = {}
for g in goals:
    importance[g] = st.slider(g, 10, 100, 50)

# ================= STRESS DIAGNOSIS =================
if st.button("1️⃣ Show stress diagnosis"):

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

    fig1, ax1 = plt.subplots()
    ax1.bar(stress_before.keys(), stress_before.values())
    ax1.set_title("Stress before optimization")
    plt.xticks(rotation=30)
    st.pyplot(fig1)

    st.info(f"Total life stress score: {total_stress_before:,.0f}")

# ================= PDF FUNCTION =================
def generate_pdf_report(data, goals, importance, optimized, improvement):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("IRMAN'S DREAM CALCULATOR – LIFE PLAN REPORT", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Planning horizon: {data['years']} years", styles["Normal"]))
    elements.append(Paragraph(f"Monthly usable surplus: ₹{data['surplus']:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Stress before optimization: {data['before']:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Stress after optimization: {data['after']:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Stress reduced by: {improvement:.1f}%", styles["Normal"]))

    elements.append(Spacer(1, 20))

    table_data = [["Goal", "Target (₹)", "Allocated (₹)", "Allocation %", "Importance %"]]
    for g in goals:
        alloc_pct = (optimized[g] / goals[g] * 100) if goals[g] > 0 else 0
        table_data.append([
            g,
            f"{goals[g]:,.0f}",
            f"{optimized[g]:,.0f}",
            f"{alloc_pct:.1f}%",
            f"{importance[g]}%"
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================= OPTIMIZATION =================
if st.button("2️⃣ Optimize my life plan"):

    if "feasible_capacity" not in st.session_state:
        st.warning("Please run stress diagnosis first")
        st.stop()

    st.balloons()

    MIN_PERCENT = 0.35
    feasible_capacity = st.session_state["feasible_capacity"]

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

    st.markdown(
        f"<h1 style='text-align:center;color:green;'>🎉 Stress Reduced by {improvement:.1f}%</h1>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Before Optimization")
        figb, axb = plt.subplots()
        axb.bar(st.session_state["stress_before"].keys(), st.session_state["stress_before"].values())
        plt.xticks(rotation=30)
        st.pyplot(figb)

    with col2:
        st.subheader("After Optimization")
        figa, axa = plt.subplots()
        axa.bar(stress_after.keys(), stress_after.values())
        plt.xticks(rotation=30)
        st.pyplot(figa)

    st.subheader("Optimized allocation summary")
    for g in goals:
        st.write(f"{g}: ₹{optimized[g]:,.0f} ({optimized[g]/goals[g]*100:.1f}%)")

    consent = st.checkbox("I allow my anonymous data to be stored for academic research")

    pdf_buffer = generate_pdf_report(
        {
            "years": horizon_years,
            "surplus": adjusted_surplus,
            "before": st.session_state["total_stress_before"],
            "after": total_stress_after
        },
        goals,
        importance,
        optimized,
        improvement
    )

    st.download_button(
        "📄 Download my optimized life report (PDF)",
        pdf_buffer,
        file_name="my_life_plan_report.pdf",
        mime="application/pdf"
    )

    if consent:
        record = {
            "timestamp": datetime.now(),
            "stress_before": st.session_state["total_stress_before"],
            "stress_after": total_stress_after,
            "improvement": improvement
        }
        df = pd.DataFrame([record])
        if not os.path.exists("responses.csv"):
            df.to_csv("responses.csv", index=False)
        else:
            df.to_csv("responses.csv", mode="a", header=False, index=False)

        st.success("Your data has been saved anonymously.")
