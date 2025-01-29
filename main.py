import streamlit as st
import pandas as pd
from datetime import datetime
import os
from pymongo import MongoClient, errors
import bcrypt
from bson import ObjectId  # Import ObjectId from bson
from streamlit_cookies_manager import EncryptedCookieManager

# Initialize the cookie manager with a password
cookies = EncryptedCookieManager(prefix="sportsbetting_", password="your_secret_password")
if not cookies.ready():
    st.stop()

# MongoDB Connection Setup
mongodb_string = st.secrets["MONGODB"]["MONGODB_STRING"]
if not mongodb_string:
    st.error("MONGODB_STRING environment variable is not set.")
    st.stop()

# Attempt to connect to MongoDB
try:
    client = MongoClient(mongodb_string, serverSelectionTimeoutMS=5000)
    client.server_info()  # Trigger a server selection to verify connection
except errors.ServerSelectionTimeoutError as err:
    st.error(f"Failed to connect to MongoDB: {err}")
    st.stop()

db = client["sportsbetting"]
users_collection = db["users"]
bets_collection = db["bets"]

# Check if the user is already logged in via cookies
if "logged_in" not in st.session_state and cookies.get("logged_in"):
    st.session_state["logged_in"] = cookies.get("logged_in") == "True"
    st.session_state["username"] = cookies.get("username")

# User Authentication
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.sidebar.header("User Authentication")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")
    register_button = st.sidebar.button("Register")

    if login_button:
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            cookies["logged_in"] = "True"  
            cookies["username"] = username
            cookies.save()  
            st.success("Login successful!")
            st.rerun()  
        else:
            st.error("Invalid credentials")

    if register_button:
        if users_collection.find_one({"username": username}):
            st.error("Username already exists")
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users_collection.insert_one({"username": username, "password": hashed_pw})
            st.success("User registered successfully! You can now log in.")
else:
    st.sidebar.header(f"Welcome, {st.session_state['username']}!")
    logout_button = st.sidebar.button("Logout")

    if logout_button:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        cookies["logged_in"] = "False"
        cookies["username"] = ""
        cookies.save()
        st.rerun()

# Ensure user is logged in before showing the betting tracker
if "logged_in" in st.session_state and st.session_state["logged_in"]:
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
                "username": st.session_state["username"],
                "date": date.strftime("%m/%d/%y"),  
                "sport": sport,
                "amount_invested": amount_invested,
                "num_picks": num_picks,
                "win_or_lose": win_or_lose,
                "amount_paid": amount_paid,
                "profit": profit
            }
            bets_collection.insert_one(new_bet)
            st.success("Bet added successfully!")

    # Display current betting data
    st.header("Your Betting Data")
    user_bets = list(bets_collection.find({"username": st.session_state["username"]}))
    if user_bets:
        bets_df = pd.DataFrame(user_bets)
        bets_df["date"] = pd.to_datetime(bets_df["date"], errors='coerce')
        bets_df["date"] = bets_df["date"].dt.strftime("%m/%d/%y")  
        bets_df = bets_df.drop(columns=["_id", "username"])  
        st.dataframe(bets_df)

        # Allow users to remove selected bets
        st.subheader("Remove Data")
        bet_to_remove = st.selectbox(
            "Select a bet to remove",
            bets_df.index,
            format_func=lambda x: f"{bets_df.iloc[x]['date']}: {bets_df.iloc[x]['sport']}, Amt: {bets_df.iloc[x]['amount_invested']}, Profit {bets_df.iloc[x]['profit']}"
        )
        if st.button("Remove Selected Bet"):
            bet_id = user_bets[bet_to_remove]["_id"]
            bets_collection.delete_one({"_id": ObjectId(bet_id)}) 
            st.success("Selected bet removed successfully!")
            st.rerun()

        total_profit = bets_df["profit"].sum()
        profit_color = "#008000" if total_profit >= 0 else "#FF0000"
        st.markdown(f"### Total Profit: <span style='color:{profit_color}; font-weight: bold;'>${total_profit:,.2f}</span>", unsafe_allow_html=True)

        st.header("Profit Tracker")
        unique_months = pd.to_datetime(bets_df["date"]).dt.to_period("M").drop_duplicates().sort_values()
        selected_month = st.selectbox("Select Month", unique_months.astype(str))

        selected_month_start = pd.Period(selected_month).start_time
        selected_month_end = pd.Period(selected_month).end_time
        filtered_data = bets_df[
            (pd.to_datetime(bets_df["date"]) >= selected_month_start) &
            (pd.to_datetime(bets_df["date"]) <= selected_month_end)
        ]

        if not filtered_data.empty:
            daily_summary = filtered_data.groupby(pd.to_datetime(filtered_data["date"]).dt.date)["profit"].sum().reset_index()
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
