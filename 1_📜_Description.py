"""
Student Financial Tracker Application

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
import time

# Page Config
st.set_page_config(
    page_title="Student Financial Tracker",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS from style.css
with open('style.css') as f:
    # Apply the custom CSS
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

sample_csv_file = (
    "https://drive.google.com/file/d/1GxjwwYY_8kFq0nPGoMmsnkc-55F9sd7J/"
    "view?usp=sharing"
)

st.title("Getting Started")
# Adding a sidebar
st.sidebar.success("Select a page above")
st.sidebar.markdown(f"[ Sample CSV file]({sample_csv_file})")

items = [
    "**Export Financial Data:** Go to your banking app or website and "
    "export your financial data as a CSV file. This file should contain "
    "details of your income and expenses.\n",
    "**Upload Data:** On the Expense Tracker, use the 'Upload CSV' button to "
    "upload the CSV file containing your financial data.\n",
    "**Enter Savings Goals:** After uploading, the program will ask you"
    "to set your savings goals. Simply enter them into the text box"
    "information.\n",
    "**Track Finances:** After uploading your data and entering savings "
    "goals, you can start tracking your finances.\n",
]

# Enumerate/add numbers before evry sentence
for idx, item in enumerate(items, start=1):
    st.markdown(f"{idx}. {item}")

#  Check session state variables if they don't exist
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

# File Upload Section
uploaded_file = st.file_uploader(label="Choose a file", type=['csv', 'xlsx'])

# Only update session state if a new file is uploaded
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.file_uploaded = True
    progress_text = "Processing your file..."
    my_bar = st.progress(0, text=progress_text)
    st.success(
        "File uploaded successfully!"
        "Please switch to the 'Overview' tab to continue.")

    # Progress bar
    for percent_complete in range(0, 101, 5):  # 5 Sterp to reduce flickering
        my_bar.progress(percent_complete,)
        time.sleep(0.1)  # Short delay for smooth updates

    # Ensure progress bar completes
    my_bar.progress(100, text="Complete!")
    st.switch_page("pages/2_📊_Overview.py")

# Once the file is uploaded successful it will show a success message
if st.session_state.get('file_uploaded', False):
    st.success("File is still available in session state.")
else:
    st.info("Please upload a CSV file to get started.")
