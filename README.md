# Sports Betting Tracker

This project is a simple and interactive sports betting tracker built with Python and Streamlit. It helps users input and monitor their betting activities, track their profits, and visualize performance over time.

## Features

1. **User Authentication**
   - Register and log in with a username and password.
   - Persistent login state using encrypted cookies.

2. **Input Betting Data**
   - Add details like the date, sport, amount invested, number of picks, win/loss status, amount paid, and profit.
   - Automatic calculation of profit based on inputs.

3. **Data Display and Management**
   - View all your bets in an interactive table.
   - Remove selected bets.
   - Download your betting data as a CSV file.

4. **Profit Visualization**
   - Plot profit over time using Streamlit's built-in graphing tools.
   - Group data by monthly intervals for better insights.

## Usage

1. **User Authentication**
   - Register a new account or log in with an existing account.
   - The login state is persisted using encrypted cookies, so you don't have to log in every time you refresh the page.

2. **Input Betting Data**
   - Use the **sidebar form** to add new betting data:
     - Enter the date of the bet.
     - Specify the sport, amount invested, number of picks, win/loss status, and amount paid.
     - Profit will be calculated automatically.

3. **View and Manage Betting Data**
   - View and analyze your betting data in the main app:
     - Review your betting history in a tabular format.
     - Remove selected bets.
     - Download your data as a CSV file.

4. **Profit Visualization**
   - Use the **Profit Tracker** section to visualize:
     - Group profit data by month.
     - Hover over points on the graph to see detailed statistics.

## File Structure

- **`main.py`**: The main Python file containing the Streamlit app logic.
- **`betting_data.csv`**: Stores the betting data locally (automatically created when you add data).
- **`.devcontainer/devcontainer.json`**: Configuration for the development container.

## Development Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/sports-betting-tracker.git
   cd sports-betting-tracker
