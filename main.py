import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Initialize the session state to store betting data if it doesn't exist
csv_file = "betting_data.csv"
if os.path.exists(csv_file):
    st.session_state.bets = pd.read_csv(csv_file)
else:
    st.session_state.bets = pd.DataFrame(columns=[
        "date", "amount_invested", "num_picks", "win_or_lose", "amount_paid", "profit"
    ])

# Sidebar for inputting data
st.sidebar.header("Add a New Bet")

with st.sidebar.form("bet_form"):
    date = st.date_input("Date", value=datetime.today())
    amount_invested = st.number_input("Amount Invested ($)", min_value=0.0, step=1.0, format="%.2f")
    num_picks = st.number_input("Number of Picks", min_value=1, step=1)
    win_or_lose = st.radio("Win or Lose", options=["Win", "Lose"])
    amount_paid = st.number_input("Amount Paid ($)", min_value=0.0, step=1.0, format="%.2f")

    # Calculate profit automatically
    profit = amount_paid - amount_invested

    submitted = st.form_submit_button("Add Bet")

    if submitted:
        # Append the new bet to the session state dataframe
        new_bet = {
            "date": date,
            "amount_invested": amount_invested,
            "num_picks": num_picks,
            "win_or_lose": win_or_lose,
            "amount_paid": amount_paid,
            "profit": profit
        }
        st.session_state.bets = pd.concat([
            st.session_state.bets, pd.DataFrame([new_bet])
        ], ignore_index=True)

        # Save to CSV
        st.session_state.bets.to_csv(csv_file, index=False)
        st.success("Bet added and saved successfully!")

# Display current betting data
st.header("Your Betting Data")

if not st.session_state.bets.empty:
    st.dataframe(st.session_state.bets)

    # Allow downloading the data as a CSV file
    csv = st.session_state.bets.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="betting_data.csv",
        mime="text/csv"
    )

    # Generate a profit-over-time graph
    st.header("Profit Tracker")

    # Convert the 'date' column to datetime
    st.session_state.bets["date"] = pd.to_datetime(st.session_state.bets["date"])

    # Let the user scroll through months and view daily profit
    unique_months = st.session_state.bets["date"].dt.to_period("M").drop_duplicates().sort_values()
    selected_month = st.selectbox("Select Month", unique_months.astype(str))

    # Filter data for the selected month
    selected_month_start = pd.Period(selected_month).start_time
    selected_month_end = pd.Period(selected_month).end_time
    filtered_data = st.session_state.bets[
        (st.session_state.bets["date"] >= selected_month_start) &
        (st.session_state.bets["date"] <= selected_month_end)
    ]

    if not filtered_data.empty:
        daily_summary = filtered_data.groupby(filtered_data["date"].dt.date)["profit"].sum().reset_index()
        daily_summary = daily_summary.rename(columns={"date": "Day", "profit": "Profit"})

        st.line_chart(
            daily_summary.set_index("Day"),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No betting data available for the selected month.")
else:
    st.info("No betting data available. Use the sidebar to add new bets.")

# Footer
st.markdown("---")
st.markdown(
    "**Sports Betting Tracker** - Created with Streamlit. Track your bets easily and visualize your profit over time!"
)
