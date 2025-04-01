import json
import datetime

FILE_PATH = 'database/db.json'

# Read data from the JSON file
def read_data():
    try:
        with open(FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"loans": [], "loan_payments": []}  # If file doesn't exist, return empty data

# Write data to the JSON file
def write_data(data):
    with open(FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

def calculate_payment_status(payment_date, due_date):
    # Calculate the difference between the due date and payment date
    delta = (payment_date - due_date).days
    
    # Determine status based on the number of days late
    if delta <= 5:
        return "On Time"  # Payment made within 5 days
    elif 6 <= delta <= 30:
        return "Late"  # Payment made between 6 and 30 days late
    elif delta > 30:
        return "Defaulted"  # Payment made more than 30 days late
    else:
        return "Unpaid"  # No payment made
