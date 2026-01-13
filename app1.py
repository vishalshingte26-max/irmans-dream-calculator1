import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="IRMAN'S DREAM CALCULATOR", layout="centered")

# ---------------- HEADER ----------------
st.title("IRMAN'S DREAM CALCULATOR")

st.markdown(
    """
This tool helps you understand how income, health, environment, family choices
and time interact with your life goals.

All calculations adjust for inflation and are based on a planning horizon you choose.
"""
)

st.markdown("---")

# ---------------- TIME HORIZON ----------------
st.subheader("Planning horizon")

horizon_years = st.slider(
    "For how many years are you planning your life goals?",
    5, 30, 10
)

st.markdown("---")

# ---------------- INCOME DETAILS ----------------
st.subheader("Income details")

salary = st.number_input(
    "Your current monthly income (₹)",
    min_value=0,
    step=5000
)

nominal_growth = st.slider(
    "Expected annual salary growth percentage (before inflation)",
    0, 15, 8
)

inflation_rate = 4
real_growth = max(nominal_growth - inflation_rate, 0)

st.info(f"After adjusting for 4% inflation, real income growth assumed: {real_growth}% per year")

expenses = st.number_input(
    "Your unavoidable monthly living expenses (₹)",
    min_value=0,
    step=2000
)

if salary <= 0:
    st.warning("Please enter income to continue.")
    st.stop()

base_surplus = salary - expenses

if base_surplus <= 0:
    st.error("Expenses exceed income. No surplus available.")
    st.stop()

st.success(f"Current monthly surplus: ₹{base_surplus:,.0f}")

st.markdown("---")

# ---------------- LIFE ASSUMPTIONS ----------------
st.subheader("Life and lifestyle assumptions (penalties are shown clearly)")

career = st.selectbox(
    "Career satisfaction and stability",
    [
        "High satisfaction (0% income penalty)",
        "Moderate satisfaction (5% income penalty)",
        "Low satisfaction (12% income penalty)"
    ]
)

health_priority = st.selectbox(
    "Health and exercise routine",
    [
        "Regular exercise and good sleep (0% penalty)",
        "Irregular routine (5% income penalty)",
        "Poor health habits (10% income penalty)"
    ]
)

aqi = st.selectbox(
    "Air quality of your living environment",
    [
        "Good AQI most of the year (0% expense penalty)",
        "Moderate AQI (4% expense penalty)",
        "Poor AQI most of the year (8% expense penalty)"
    ]
)

family_setup = st.selectbox(
    "Living arrangement",
    [
        "Living with family (5% lower expenses)",
        "Living away from family (5% higher expenses)"
    ]
)

work_style = st.selectbox(
    "Work pattern",
    [
        "Balanced and sustainable (0% penalty)",
        "Aggressive long hours (8% income boost, burnout risk)",
        "Frequent burnout cycles (12% income penalty)"
    ]
)

st.markdown("---")

# ---------------- PENALTIES ----------------
income_penalty = 0.0
expense_penalty = 0.0

if "Moderate" in career:
    income_penalty += 0.05
elif "Low" in career:
    income_penalty += 0.12

if "Irregular" in health_priority:
    income_penalty += 0.05
elif "Poor" in health_priority:
    income_penalty += 0.10

if "Moderate AQI" in aqi:
    expense_penalty += 0.04
elif "Poor AQI" in aqi:
    expense_penalty += 0.08

if "with family" in family_setup:
    expense_penalty -= 0.05
elif "away" in family_setup:
    expense_penalty += 0.05

if "Aggressive" in work_style:
    income_penalty -= 0.08
elif "burnout" in work_style.lower():
    income_penalty += 0.12

adjusted_income = salary * (1 - income_penalty)
adjusted_expenses = expenses * (1 + expense_penalty)
adjusted_surplus = adjusted_income - adjusted_expenses

st.subheader("Net impact of your choices")

st.write(f"Total income penalty applied: {income_penalty*100:.1f}%")
st.write(f"Total expense penalty applied: {expense_penalty*100:.1f}%")
st.info(f"Usable monthly surplus after adjustments: ₹{adjusted_surplus:,.0f}")

st.markdown("---")

# ---------------- GOALS ----------------
st.subheader("Life goals")

house = st.number_input("House or flat purchase (₹)", 0, step=100000)
land = st.number_input("Land purchase (₹)", 0, step=100000)
vehicle = st.number_input("Vehicle purchase (₹)", 0, step=50000)

asset_goal = house + land + vehicle

goals = {}
goals["Asset creation"] = asset_goal
goals["Emergency fund"] = st.number_input("Emergency fund target (₹)", 0, step=50000)
goals["Education or loan repayment"] = st.number_input("Education or loan repayment target (₹)", 0, step=50000)
goals["Marriage and family setup"] = st.number_input("Marriage and family setup target (₹)", 0, step=50000)
goals["Social contribution"] = st.number_input("Social contribution target (₹)", 0, step=20000)

st.markdown("---")

# ---------------- IMPORTANCE ----------------
st.subheader("If delayed, how stressful would each goal be?")

weights = {}
for g in goals:
    weights[g] = st.slider(g, 1, 5, 3)

st.markdown("---")

# ---------------- RESULTS ----------------
if st.button("Show results"):

    feasible_capacity = max(adjusted_surplus * 12 * horizon_years, 0)
    equal_share = feasible_capacity / len(goals)

    deviations = {}
    weighted_deviation = {}

    for g in goals:
        gap = max(goals[g] - equal_share, 0)
        deviations[g] = gap
        weighted_deviation[g] = gap * weights[g]

    st.subheader("Where pressure appears")

    for g in deviations:
        if deviations[g] > 0:
            monthly_gap = deviations[g] / (horizon_years * 12)
            st.write(
                f"{g} is short by ₹{deviations[g]:,.0f}, "
                f"or ₹{monthly_gap:,.0f} per month"
            )

    fig, ax = plt.subplots()
    ax.bar(weighted_deviation.keys(), weighted_deviation.values())
    ax.set_ylabel("Stress level")
    ax.set_title("Pressure across life goals")
    plt.xticks(rotation=30)
    st.pyplot(fig)

    st.markdown("---")

    # ---------------- TRADE OFF OPTIONS ----------------
    st.subheader("Trade off options")

    for g in deviations:
        if deviations[g] > 0:
            monthly_gap = deviations[g] / (horizon_years * 12)
            percent_of_goal = (monthly_gap * 12 * horizon_years / goals[g]) * 100 if goals[g] > 0 else 0
            extra_years = deviations[g] / (adjusted_surplus * 12) if adjusted_surplus > 0 else 0

            st.markdown(f"**{g}**")
            st.write(f"Unmet amount per month: ₹{monthly_gap:,.0f}")
            st.write(f"Reducing this goal by {percent_of_goal:.1f}% will fully remove this gap")
            st.write(f"Increasing planning horizon by about {extra_years:.1f} years will also remove the gap")
            st.write("You may also offset this gap by reallocating savings from lower priority goals")

