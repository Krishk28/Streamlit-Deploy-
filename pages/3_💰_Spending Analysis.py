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

st.title("Spending Analysis")

# Ensures the file is still in session state and does not reset file
if not st.session_state.get('uploaded_file'):
    st.info("Please upload a CSV file to get started.")
    st.stop()

# Get the uploaded file from session state
uploaded_file = st.session_state.uploaded_file


# Attempt to read the CSV file only if it's not empty
if uploaded_file:
    try:
        # File reset so it doesnt interfere with other components of code
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, skiprows=6, skip_blank_lines=True,)

    except Exception as e:
        st.error(
            f"Error reading the file: {e}. "
            "Trying to determine the delimiter..."
        )
        # If failed try different delimiters
        success = False
        for delimiter in [',', ';', '\t']:
            # Enter a loop reading the file with different delimiters
            try:
                # Reset the file before each attempt
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file, delimiter=delimiter, skiprows=6)
                # Skip the first six rows and avoid 'bad lines'
                success = True
                break  # Exit the loop upon success
            except Exception as e:
                st.warning(
                    f"Error reading as"
                    f"{delimiter}-delimited CSV: {e}"
                )

        if not success:
            st.error(
                "Attempts to read the file failed."
                "Please upload a valid CSV file.")
            df = None


if df is not None and not df.empty:
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

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

    # Create a new column for Month and Day of the Week
    df_outflow['Month'] = df_outflow['Date'].dt.month_name()
    df_outflow['Day of Week'] = df_outflow['Date'].dt.day_name()

    # Calculate monthly total expenses
    df_outflow['total_expenses'] = df_outflow['Amount']

    # Allocate spending by month
    monthly_spending = df_outflow.groupby(
        'Month')['total_expenses'].sum().reset_index()

    # The correct order of months
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September',
        'October', 'November', 'December'
    ]

    # Convert 'Month' column to have a specified order
    monthly_spending['Month'] = pd.Categorical(
        monthly_spending['Month'], categories=month_order, ordered=True)
    monthly_spending = monthly_spending.sort_values('Month')

    # Aggregate spending by day of the week
    weekly_spending = df_outflow.groupby(
        'Day of Week')['total_expenses'].sum().reset_index()
    # Order the days
    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_spending['Day of Week'] = pd.Categorical(
        weekly_spending['Day of Week'], categories=days_order, ordered=True)
    weekly_spending = weekly_spending.sort_values('Day of Week')

    # Convert negative amounts to positive for proper display
    monthly_spending['total_expenses'] = monthly_spending['total_expenses'].abs()

    weekly_spending['total_expenses'] = weekly_spending['total_expenses'].abs()

    # Plot Monthly Spending
    st.subheader("Monthly Spending Analysis")
    fig_monthly = px.bar(
        monthly_spending,
        x='Month',
        y='total_expenses',
        labels={'Month': 'Month',
                'total_expenses': 'Total Spending'},
        title='Total Monthly Spending'
    )
    st.plotly_chart(fig_monthly)

    # Create an expander for the DataFrame
    with st.expander("View Monthly Spending Data", expanded=False):
        # Make the DataFrame horizontal
        transposed_monthly_spending = monthly_spending.set_index('Month').T
        st.dataframe(transposed_monthly_spending, use_container_width=True)

    # Plot Weekly Spending
    st.subheader("Weekly Spending Analysis")
    fig_weekly = px.bar(
        weekly_spending,
        x='Day of Week',
        y='total_expenses',
        labels={'Day of Week': 'Day of Week',
                'total_expenses': 'Total Spending'},
        title='Total Spending by Day of the Week'
    )
    st.plotly_chart(fig_weekly)

    # Create an expander for the DataFrame
    with st.expander("View Weekly Spending Data", expanded=False):
        # Make the DataFrame horizontal
        tranposed_weekly_spending = weekly_spending.set_index('Day of Week').T
        st.dataframe(tranposed_weekly_spending, use_container_width=True)


st.divider()


# Button to toggle the display of the DataFrame
# Check if the DataFrame (df) has been loaded and is not empty
if df is not None and not df.empty:
    if 'show_dataframe' not in st.session_state:
        st.session_state.show_dataframe = False

    # Toggle button
    if st.button("Toggle DataFrame"):
        st.session_state.show_dataframe = not st.session_state.show_dataframe

    # DataFrame displayed based on st.session_state.show_dataframe.
    if st.session_state.show_dataframe:
        st.write(df)

# Indicate that the file is available in session state
st.markdown('`File is available in session state.`')
