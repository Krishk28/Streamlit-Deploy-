"""
Student Financial Tracker Application.

This Streamlit app lets students upload and analyze their financial data.
Features include:

- Displaying balance, total income, and total expenses.
- Filtering transactions by date.
- Tracking progress towards savings goals.
- Visualizing expenses by category and comparing income vs. expenses.
- Viewing raw transaction data.

Supports CSV file uploads.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Student Financial Tracker",
    page_icon="📊",
    layout="wide"
)

sample_csv_file = (
    "https://drive.google.com/file/d/1GxjwwYY_8kFq0nPGoMmsnkc-55F9sd7J/"
    "view?usp=sharing"
)

# Load the CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.title("Overview")
st.sidebar.markdown(f"[Sample CSV file]({sample_csv_file})")

# Ensures the file is still in session state and does not reset file
if not st.session_state.get('uploaded_file'):
    st.info("Please upload a CSV file to get started.")
    st.stop()

# Get the uploaded file from session state
uploaded_file = st.session_state.uploaded_file

# Initialize variables
balance_value = "N/A"
total_expenses = 0
df = None
df_filtered = None

# Read the CSV file only if it's not empty
if uploaded_file:
    try:
        # File reset so it doesnt interfere with other components of code
        uploaded_file.seek(0)
        content = uploaded_file.read().decode('utf-8')  # Read the file as text
        lines = content.splitlines()

        for line in lines:  # look for Avail Bal in the csv file
            if "Avail Bal" in line:
                # Extract the data before ' as of'
                end_index = line.find(' as of')
                # Display the data before ' as of'
                balance_part = line[:end_index]
                balance_value = balance_part.split(
                    ':')[1].strip()  # only extract after the : sign
                break

        uploaded_file.seek(0)
        # Try read the CSV file
        df = pd.read_csv(uploaded_file, skiprows=6,)

    except Exception as e:
        st.error(
            f"Error reading the file: {e}. "
            "Trying to determine the delimiter..."
        )

        # If failed try different delimiters
        success = False
        for delimiter in [',', ';', '\t']:
            # Enter a loop trying reading the file with different delimiters
            try:
                # Reset the file before each attempt
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file, delimiter=delimiter, skiprows=6)
                # Skip the first six rows and avoid 'bad lines'
                success = True
                break  # Exit the loop upon success
            except Exception as e:
                st.warning(f"Error reading as {delimiter}-delimited CSV: {e}")

        if not success:
            st.error(
                "Attempts to read the file failed."
                "Please upload a valid CSV file.")
            df = None


if df is not None and not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

    # Set start and end date for the date inputs
    start_date = df["Date"].min()
    end_date = df["Date"].max()

    # Put the date selecters in the sidebar
    st.sidebar.subheader("Filter Data by Date")
    date1 = st.sidebar.date_input("Start Date", start_date)
    date2 = st.sidebar.date_input("End Date", end_date)

    # Telling the user the period
    st.markdown(f"`For Period of {date1} to {date2}`")

    # Filter DataFrame based on selected date range
    df_filtered = df[(df["Date"] >= pd.to_datetime(date1)) &
                     (df["Date"] <= pd.to_datetime(date2))].copy()

    # Filter by cash outflow transaction types
    cash_outflow_trantypes = ['D/D', 'INT', 'DEBIT', 'EFTPOS', 'BILLPAY']
    df_outflow = df_filtered[df_filtered['Tran Type'].isin(
        cash_outflow_trantypes)]

    # Calculate total expenses after filtering
    total_expenses = df_outflow[df_outflow['Amount'] < 0]['Amount'].sum()
    formatted_total_expenses = (
        f"${total_expenses:.2f}"
        if total_expenses >= 0
        else f"-${abs(total_expenses):,.2f}"
    )

    # Filter by cash inflow transaction types
    cash_inflow_trantypes = ['CREDIT', 'DEPOSIT', 'INT', 'TFR IN', 'D/C']
    df_inflow = df_filtered[df_filtered['Tran Type'].isin(
        cash_inflow_trantypes)]

    # Calculate total income after filtering
    total_income = df_inflow[df_inflow['Amount'] > 0]['Amount'].sum()
else:
    st.error("Improper File Format")

st.markdown("#####")

# Creating a container for the Current Balance
with st.container():
    col1, col2, col3, = st.columns(3)

    # Balance Column
    with col1:
        st.markdown(
            f"""
      <div class="container">
            <div class="metric-label">Available Balance:</div>
            <div class="metric-value">${balance_value}</div>
        </div>
        """,
            unsafe_allow_html=True
        )

    # Expense Column
    with col2:
        st.markdown(
            f"""
            <div class="container">
                <div class="metric-label">Total Expenses:</div>
                <div class=
                "metric-value total-expenses">{formatted_total_expenses}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Income Column
    with col3:
        st.markdown(
            f"""
            <div class="container">
                <div class="metric-label">Total Income:</div>
                <div class=
                "metric-value total-income">+${total_income:.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Savings Goal container
with st.container():
    # Input for Savings Goal
    savings_goal = st.number_input(
        "Enter Your Savings Goal", min_value=0.0, value=0.0, step=100.0)

    if balance_value != "N/A":
        # Convert to a float to remove commas and dollar signs
        available_balance = float(
            balance_value.replace('$', '').replace(',', ''))

        # Show Savings Progress if the user has set a goal
        if savings_goal > 0:
            # Calculate the percentage
            progress = (available_balance / savings_goal) * 100
            # Clamp the progress between [0, 100]
            progress = min(max(progress, 0), 100)

            # Display the progress
            st.markdown(
                f'<div class="progress-text">'
                f'Your progress: <code>{progress:.2f}%</code>'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="progress-difference">'
                f'${available_balance:,.2f} / ${savings_goal:,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.progress(progress / 100)  # Convert to fraction (0.0 to 1.0)

        else:
            st.warning("Please set a savings goal to see your progress.")
    else:
        st.warning("No balance information available.")

st.divider()

# Pie Chart
if 'show_dataframe' not in st.session_state:
    st.session_state.show_dataframe = False

payee_summary = df_outflow.groupby("Payee")["Amount"].sum().reset_index()

with st.container():
    st.subheader("Expense Breakdown")
    # Checks if payee_summary has data
    if not payee_summary.empty:
        # only include rows where the "Amount" is negative ie expenses
        payee_summary = payee_summary[payee_summary["Amount"] < 0]

        if payee_summary.empty:
            # If payee_summary is empty after filtering show a error
            st.warning("No expense data available for the selected payees.")
        else:
            # Plot using absolute values but indicate they are expenses
            payee_summary["Amount Absolute"] = payee_summary["Amount"].abs()

            fig = px.pie(
                payee_summary,
                values='Amount Absolute',  # Uses absolute values for the pie
                names='Payee',  # Labels with the payee’s name
                title="",
                labels=payee_summary.set_index('Payee')['Amount'].apply(
                    # Format with a dollar sign and two decimal places.
                    lambda x: f"-${abs(x):,.2f}"
                ).to_dict()
            )
            fig.update_traces(textinfo='label+percent', textposition='inside')
            # Ensure the legend is shown
            fig.update_layout(showlegend=True)
            # Displays the pie chart
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(
            "No data available to display."
            "Please check your file format and content.")

st.divider()

with st.container():
    st.subheader("Expenses Vs Income")
    # Create a DataFrame for total expenses and total income
    if df_filtered is not None and not df_filtered.empty:
        # Create an DataFrame to hold dates from filtered data
        # each date only comes once
        cash_flow_data = df_filtered[['Date']].drop_duplicates().copy()

        # Calculates the total expenses for each day
        total_expenses_daily = df_outflow.groupby(
            'Date')['Amount'].sum().abs().reset_index()
        total_expenses_daily.columns = [
            'Date', 'Total Expenses']  # Columns Renamed

        # Calculates the total income for each day
        total_income_daily = df_inflow.groupby('Date')['Amount'].sum().reset_index()
        total_income_daily.columns = ['Date', 'Total Income']  # Rename columns

        # Merged _daily values into the cash_flow_data DataFrame
        cash_flow_data = cash_flow_data.merge(
            total_expenses_daily, on='Date', how='left')
        cash_flow_data = cash_flow_data.merge(
            total_income_daily, on='Date', how='left')

        # For dates without have data for expenses or income set it as 0
        cash_flow_data['Total Expenses'] = cash_flow_data['Total Expenses'].fillna(
            0)

        cash_flow_data['Total Income'] = cash_flow_data['Total Income'].fillna(
            0)

        cash_flow_data['Total Expenses'] = cash_flow_data['Total Expenses'].rolling(window=5, min_periods=1).mean()
        cash_flow_data['Total Income'] = cash_flow_data['Total Income'].rolling(window=5, min_periods=1).mean()

        # Create the line chart using Plotly Express
        fig = px.line(
            cash_flow_data,
            x='Date',
            y=['Total Income', 'Total Expenses'],
            labels={'value': 'Amount ($)', 'variable': 'Transaction Type'},
            markers=True  # Add markers for better visualization
        )

        # Update the colors of the lines
        fig.update_traces(
            line=dict(color='chartreuse'),  # Set income line to green
            selector=dict(name='Total Income')
        )
        fig.update_traces(
            line=dict(color='red'),  # Set expenses line to red
            selector=dict(name='Total Expenses')
        )

        # Customize hover pop up to show only Date and Amount
        fig.for_each_trace(
            lambda trace: trace.update(
                hovertemplate='Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>'
            )
        )

        #  layout features
        fig.update_layout(
            hovermode="x unified",  # Info when you hover
            xaxis=dict(showgrid=True),  # Adding gridlines
            yaxis=dict(showgrid=True),  # Adding gridlines
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            template='plotly_white',
        )

    # Display the line chart
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(
            "No income or expense data available for the selected date range.")


st.divider()

# Button to toggle the display of the DataFrame
# Check if the DataFrame (df) has been loaded and is not empty
if df is not None and not df.empty:
    if 'show_dataframe' not in st.session_state:
        st.session_state.show_dataframe = False

    # Toggle button
    if st.button("Toggle DataFrame"):
        st.session_state.show_dataframe = not st.session_state.show_dataframe

    #  DataFrame displayed based on st.session_state.show_dataframe
    if st.session_state.show_dataframe:
        st.write(df)

# Indicate that the file is available in session state
st.markdown('`File is available in session state.`')
