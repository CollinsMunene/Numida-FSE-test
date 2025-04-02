from datetime import datetime, date
import time
from flask import Flask, request,jsonify
# Usage of Ariadne as it's compatible with latest version of graphql-core(3.2.5)
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
        amount: Float!
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
    
    input LoanFilter {
        id:Int
        name: String
        due_date: Date
    }
                
    input LoanPaymentFilter{
        id:Int
        status: String
        loan_id: Int
    }
    
    type Query {
        loans(filters: LoanFilter,isCombined:Boolean!): [Loan!]!
        loanPayments(filters: LoanPaymentFilter): [LoanPayment!]!
    }
    
    type Mutation {
        updateLoan(loan_id: Int!): Loan!
        deleteLoan(loan_id: Int!): Boolean!
    }
    
""")

# Define resolvers
query = ObjectType("Query")
mutation = ObjectType("Mutation")

@query.field("loans")
def resolve_loans(*_,filters=None,isCombined=False):
    try:
        time.sleep(1)
        data = read_data()
        loans = data.get("loans", [])

        if filters:
            if filters.get("id"):
                loans = [loan for loan in loans if loan["id"] == filters["id"]]
           
            if filters.get("name"):
                loans = [loan for loan in loans if filters["name"].lower() in loan["name"].lower()]

            if filters.get("due_date"):
                loans = [loan for loan in loans if loan["due_date"] == filters["due_date"]]

        # Check if the results needed should be combined
        if isCombined:
            for loan in loans:
                # Find the latest payment for the loan
                payment = next((payment for payment in data.get("loan_payments", []) if payment["loan_id"] == loan["id"]), None)

                if payment:
                    # Add the payment details into the loan object
                    loan["payment_date"] = payment["payment_date"]
                    loan["status"] = payment['status']
                else:
                    # If no payment found, set status to 'Unpaid'
                    loan["payment_date"] = None
                    loan["status"] = "Unpaid"

            return loans
        else:
            # Else return the whole loan object
            for loan in loans:
                loan["payments"] = [payment for payment in data.get("loan_payments", []) if payment["loan_id"] == loan["id"]]
            return loans
    except Exception as e:
        print(f"Error in resolve_loans: {e}")
        raise Exception("Failed to retrieve loans")

@query.field("loanPayments")
def resolve_loanPayments(*_, filters=None):
    try:
        time.sleep(1)
        data = read_data()
        loan_payments = data.get("loan_payments", [])

        if filters:
            if filters.get("id"):
                loan_payments = [loan_payment for loan_payment in loan_payments if loan_payment["id"] == filters["id"]]
            
            if filters.get("status"):
                loan_payments = [loan_payment for loan_payment in loan_payments if loan_payment["status"] == filters["status"]]
            
            if filters.get("loan_id"):
                loan_payments = [loan_payment for loan_payment in loan_payments if loan_payment["loan_id"] == filters["loan_id"]]

        for payment in loan_payments:
            payment["loan"] = next((loan for loan in data.get("loans", []) if loan["id"] == payment["loan_id"]), None)

        return loan_payments

    except Exception as e:
        print(f"Error in resolve_loanPayments: {e}")
        raise Exception("Failed to retrieve loan payments")


@mutation.field("updateLoan")
def resolve_update_loan(_, info, loan_id):  
    try:
        data = read_data()
        loan = next((loan for loan in data.get("loans", []) if loan["id"] == loan_id), None)

        if not loan:
            raise Exception("Loan not found")

        if loan["status"] in ["Draft","Submitted"]: 
            if request.json.get("due_date"):
                try:
                    due_date = datetime.strptime(request.json["due_date"], "%Y-%m-%d").date()
                    loan["due_date"] = due_date
                except ValueError as e:
                    print(f"Error parsing due_date: {e}")
                    raise Exception("Invalid due date format")

            if request.json.get("name"):
                loan["name"] = request.json["name"]

            write_data(data)
            return loan
        else:
            raise Exception("Loan cannot be updated")
    except Exception as e:
        print(f"Error in updateLoan: {e}")
        raise Exception("Failed to update loan payment")

@mutation.field("deleteLoan")
def resolve_delete_loan(_, info, loan_id):  
    try:
        data = read_data()
        loan = next((loan for loan in data.get("loans", []) if loan["id"] == loan_id), None)

        if not loan:
            raise Exception("Loan not found")

        if loan["status"] in ["Draft","Submitted"]: 
            data.setdefault("loan_payments", []).remove(loan)

            write_data(data)
            return loan
        else:
            raise Exception("Loan cannot be deleted")
    except Exception as e:
        print(f"Error in addLoanPayment: {e}")
        raise Exception("Failed to add loan payment")

# Same executable schema
schema = make_executable_schema(type_defs, [query,mutation, date_scalar])

explorer_html = ExplorerGraphiQL(
    title="Collins Numida Playground"
).html(None)

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
        time.sleep(3)
        payment_data = request.json

        data = read_data()
        loan = next((loan for loan in data.get("loans", []) if loan["id"] == payment_data.get("loan_id")), None)

        if not loan:
            raise Exception("Loan not found")

        if not payment_data.get("amount") or payment_data.get("amount") <= 0:
            raise Exception("Amount not sufficient to deposit")

        try:
            due_date = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Error parsing due_date: {e}")
            raise Exception("Invalid due date format")

        # Geting today's date as the payment date
        payment_date = date.today()

        # Let's compute the payment status
        payment_status = calculate_payment_status(payment_date, due_date)

        # Increment ID safely
        new_id = max((payment["id"] for payment in data.get("loan_payments", [])), default=0) + 1

        # Create the new payment entry
        new_payment = {
            "id": new_id,
            "loan_id": payment_data.get("loan_id"),
            "amount":payment_data.get("amount",0),
            "payment_date": payment_date.isoformat(),
            "status": payment_status
        }

        data.setdefault("loan_payments", []).append(new_payment)

        write_data(data)
        return new_payment
    except Exception as e:
        print(f"Error in addLoanPayment REST: {e}")
        raise Exception("Failed to add loan payment va REST")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)