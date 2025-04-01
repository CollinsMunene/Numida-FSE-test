from datetime import datetime, date
from flask import Flask, request,jsonify
# Usage of Ariadne asit's compatible with latest version of graphql-core(3.2.5)
from ariadne import graphql_sync, make_executable_schema, ObjectType, gql, ScalarType 
from ariadne.explorer import ExplorerGraphiQL
from flask_cors import CORS

# Let's use file storage as our test database
from utilities.utility import calculate_payment_status, read_data, write_data

app = Flask(__name__)
CORS(app)

# Re-Define schema using SDL (Schema Definition Language)
# Date scalar is custom, we will need to handle it's parsing
date_scalar = ScalarType("Date")

@date_scalar.serializer
def serialize_date(value):
    if isinstance(value, date):
        return value.isoformat()  # Converts Python date to string (YYYY-MM-DD),  used during queries
    return value 

@date_scalar.value_parser
def parse_date_value(value):
    return datetime.strptime(value, "%Y-%m-%d").date()  # Converts string → Python date, used during mutations

@date_scalar.literal_parser
def parse_date_literal(ast):
    return datetime.strptime(ast.value, "%Y-%m-%d").date()  # Converts AST (Abstract Syntax Tree) → Python date, used when date is on params in mutations


type_defs = gql("""
    scalar Date 
    
    type LoanPayment {
        id: Int!
        loan_id: Int!
        loan: Loan
        payment_date: Date! 
        status: String!    
    }
    
    type Loan {
        id: Int!
        name: String!
        interest_rate: Float!
        principal: Int!
        due_date: Date!
        payments: [LoanPayment!]
        payment_date: Date
        status: String
    }
    
    type Query {
        loans(isCombined:Boolean!): [Loan!]!
        loanPayments: [LoanPayment!]!
    }
    
    type Mutation {
        addLoanPayment(loan_id: Int!): LoanPayment!
    }
    
""")

# Define resolvers
query = ObjectType("Query")
mutation = ObjectType("Mutation")

@query.field("loans")
def resolve_loans(*_,isCombined=False):
    try:
        # Resolving 'payments' field of Loan
        data = read_data()
        if isCombined:
             # Iterate through the loans
            for loan in data.get("loans", []):
                # Find the latest payment for the loan (assuming one payment for simplicity)
                payment = next((payment for payment in data.get("loan_payments", []) if payment["loan_id"] == loan["id"]), None)

                if payment:
                    # Add the payment details into the loan object
                    loan["payment_date"] = payment["payment_date"]
                    loan["status"] = payment['status']  # The calculated status
                else:
                    # If no payment found, set status to 'Unpaid'
                    loan["payment_date"] = None
                    loan["status"] = "Unpaid"

            return data["loans"]

        else:
            for loan in data.get("loans", []):  # Using `.get()` to avoid KeyError
                loan["payments"] = [payment for payment in data.get("loan_payments", []) if payment["loan_id"] == loan["id"]]
            return data["loans"]
    except Exception as e:
        print(f"Error in resolve_loans: {e}")
        raise Exception("Failed to retrieve loans")  # Generic error message for GraphQL response


@query.field("loanPayments")
def resolve_loanPayments(*_):
    try:
        # Resolving 'loan_id' to return the full Loan object
        data = read_data()
        for payment in data.get("loan_payments", []):
            payment["loan"] = next((loan for loan in data.get("loans", []) if loan["id"] == payment["loan_id"]), None)
        return data["loan_payments"]

    except Exception as e:
        print(f"Error in resolve_loanPayments: {e}")
        raise Exception("Failed to retrieve loan payments")


@mutation.field("addLoanPayment")
def resolve_add_loan_payment(_, info, loan_id):  
    try:
        data = read_data()
        loan = next((loan for loan in data.get("loans", []) if loan["id"] == loan_id), None)

        if not loan:
            raise Exception("Loan not found")  # Handle missing loan case

        # Extract the due date from the loan data
        try:
            due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Error parsing due_date: {e}")
            raise Exception("Invalid due date format")

        # Get today's date as the payment date
        payment_date = date.today()

        # Compute the payment status
        payment_status = calculate_payment_status(payment_date, due_date)

        # Increment ID safely
        new_id = max((payment["id"] for payment in data.get("loan_payments", [])), default=0) + 1

        # Create the new payment entry
        new_payment = {
            "id": new_id,
            "loan_id": loan_id,
            "payment_date": payment_date.isoformat(),
            "status": payment_status
        }

        # Add the new payment to the loan_payments list
        data.setdefault("loan_payments", []).append(new_payment)

        # Write the updated data back to the JSON file
        write_data(data)

        return new_payment
    except Exception as e:
        print(f"Error in addLoanPayment: {e}")
        raise Exception("Failed to add loan payment")

# Same executable schema
schema = make_executable_schema(type_defs, [query,mutation, date_scalar])

explorer_html = ExplorerGraphiQL().html(None)

# Return Playground on GET
@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    return explorer_html, 200

# Return normal data on POST
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.route("/")
def home():
    return "Welcome to the Loan Application API"

@app.route("/make_payment",methods=["POST"])
def AddLoanPayment():
    try:
        payment_data = request.json  # Assuming the data is sent in JSON format

        data = read_data()
        loan = next((loan for loan in data.get("loans", []) if loan["id"] == payment_data.get("loan_id")), None)

        if not loan:
            raise Exception("Loan not found")  # Handle missing loan case

        # Extract the due date from the loan data
        try:
            due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Error parsing due_date: {e}")
            raise Exception("Invalid due date format")

        # Get today's date as the payment date
        payment_date = date.today()

        # Compute the payment status
        payment_status = calculate_payment_status(payment_date, due_date)

        # Increment ID safely
        new_id = max((payment["id"] for payment in data.get("loan_payments", [])), default=0) + 1

        # Create the new payment entry
        new_payment = {
            "id": new_id,
            "loan_id": payment_data.get("loan_id"),
            "payment_date": payment_date.isoformat(),
            "status": payment_status
        }

        # Add the new payment to the loan_payments list
        data.setdefault("loan_payments", []).append(new_payment)

        # Write the updated data back to the JSON file
        write_data(data)

        return new_payment
    except Exception as e:
        print(f"Error in addLoanPayment REST: {e}")
        raise Exception("Failed to add loan payment va REST")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)