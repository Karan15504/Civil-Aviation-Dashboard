# Civil-Aviation-Dashboard
✈️ Indian Civil Aviation Route Analysis
📌 Project Overview
This project analyzes domestic civil aviation traffic and passenger data across various Origin-Destination (OD) pairs. It features an automated data pipeline that ingests raw airline data, cleans formatting inconsistencies (such as removing auto-generated summary rows), and prepares the dataset for deeper analysis or database storage.

✨ Key Features
Automated Data Cleaning: Uses Python to strip out blank rows, trailing spaces, and standardizes city names.

OD Pair Tracking: Validates and filters specific flight routes (e.g., ADAMPUR-Ghaziabad, MUMBAI-LUCKNOW).

Traffic Aggregation: Calculates accurate passenger/cargo loads without relying on pre-calculated Excel sub-totals.

Database Ready: Formats the cleaned DataFrame for seamless export to relational databases.
