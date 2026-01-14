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

# =====
