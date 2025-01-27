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
        "date", "sport" ,"amount_invested", "num_picks", "win_or_lose", "amount_paid", "profit"
    ])

# Sidebar for inputting data
st.sidebar.header("Add a New Bet")

with st.sidebar.form("bet_form"):
    date = st.date_input("Date", value=datetime.today())
    sport = st.text_input("Sport", placeholder="Enter the sport you bet on")
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
            "sport": sport,
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

# Import data from a CSV file
st.sidebar.header("Import Betting Data")
imported_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
if imported_file is not None:
    try:
        imported_data = pd.read_csv(imported_file)
        if set(["date", "sport", "amount_invested", "num_picks", "win_or_lose", "amount_paid", "profit"]).issubset(imported_data.columns):
            imported_data["date"] = pd.to_datetime(imported_data["date"], errors='coerce')
            st.session_state.bets = imported_data  # Overwrite existing data
            st.session_state.bets.to_csv(csv_file, index=False)
            st.success("Data imported successfully and overwritten!")
        else:
            st.error("The uploaded CSV does not have the required columns.")
    except Exception as e:
        st.error(f"An error occurred while importing data: {e}")

# Display current betting data
st.header("Your Betting Data")

if not st.session_state.bets.empty:
    # Reorder columns to have 'sport' next to 'date'
    reordered_columns = ["date", "sport", "amount_invested", "num_picks", "win_or_lose", "amount_paid", "profit"]
    st.session_state.bets = st.session_state.bets[reordered_columns]
    
    st.dataframe(st.session_state.bets)

    # Option to remove rows
    st.subheader("Remove Data")
    indices_to_remove = st.multiselect("Select rows to remove:", st.session_state.bets.index, format_func=lambda x: f"Date: {st.session_state.bets.iloc[x]['date']}, Sport: {st.session_state.bets.iloc[x]['sport']}, Amount Invested: {st.session_state.bets.iloc[x]['amount_invested']}, Picks: {st.session_state.bets.iloc[x]['num_picks']}, Result: {st.session_state.bets.iloc[x]['win_or_lose']}, Amount Paid: {st.session_state.bets.iloc[x]['amount_paid']}, Profit: {st.session_state.bets.iloc[x]['profit']}")
    if st.button("Remove Selected Rows", key="remove_rows_button"):
        if indices_to_remove:
            st.session_state.bets.drop(indices_to_remove, inplace=True)
            st.session_state.bets.reset_index(drop=True, inplace=True)
            st.session_state.bets.to_csv(csv_file, index=False)
            st.success("Selected rows removed and data updated successfully!")
            st.rerun()

     # Display total profit below the table
    total_profit = st.session_state.bets["profit"].sum()
    profit_color = "#008000" if total_profit >= 0 else "#FF0000"
    st.markdown(f"### Total Profit: <span style='color:{profit_color}; font-weight: bold;'>${total_profit:,.2f}</span>", unsafe_allow_html=True)

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
