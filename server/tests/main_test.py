from datetime import date
import pytest
from unittest.mock import patch
from app import app,resolve_loans
from flask.testing import FlaskClient

mock_data = {
    "loans": [
        {
            "id": 1,
            "name": "Tom's Loan",
            "interest_rate": 5.0,
            "principal": 10000,
            "due_date": "2025-03-01",
            "status": "Approved"
        },
        {
            "id": 2,
            "name": "Chris Wailaka",
            "interest_rate": 3.5,
            "principal": 500000,
            "due_date": "2025-03-01",
            "status": "Approved"
        }
    ],
    "loan_payments": [
        {
            "id": 1,
            "loan_id": 1,
            "payment_date": "2024-03-04",
            "amount": 100,
            "status": "On Time"
        },
        {
            "id": 2,
            "loan_id": 2,
            "payment_date": "2024-03-04",
            "amount": 100,
            "status": "On Time"
        }

    ]
}

@pytest.fixture
def mock_read_data():
    """We will Mock the read_data function to return out custom data above."""
    with patch("app.read_data", return_value=mock_data):
        yield

@pytest.fixture
def client() -> FlaskClient:
    """This is a test client for Flask."""
    with app.test_client() as client:
        yield client


def test_resolve_loans_no_filter(mock_read_data):
    """Test: Fetching all loans without filters."""
    result = resolve_loans()
    assert len(result) == 2

def test_resolve_loans_with_id_filter(mock_read_data):
    """Test: Filtering by loan ID."""
    result = resolve_loans(filters={"id": 1})
    assert len(result) == 1
    assert result[0]["name"] == "Tom's Loan"

def test_resolve_loans_with_name_filter(mock_read_data):
    """Test: Filtering by loan name"""
    result = resolve_loans(filters={"name": "Chris Wailaka"})
    assert len(result) == 1
    assert result[0]["id"] == 2

def test_resolve_loans_with_due_date(mock_read_data):
    """Test: Filtering by due date."""
    result = resolve_loans(filters={"due_date": "2025-03-01"})
    assert len(result) == 2
    assert result[0]["id"] == 1

def test_resolve_loans_combined(mock_read_data):
    """Test: Send 'isCombined=True' where we need to merge loan & payment data."""
    result = resolve_loans(isCombined=True)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["due_date"] == "2025-03-01"
    assert result[0]["status"] == "On Time"
    assert result[1]["payment_date"] == "2024-03-04"
    assert result[1]["status"] == "On Time"

def test_resolve_loans_no_matching_results(mock_read_data):
    """Test: When filters return no results."""
    result = resolve_loans(filters={"id": 999})
    assert result == []

def test_resolve_loans_exception_handling(mock_read_data):
    """Test: Incase of an exception if it has been handled properly."""
    with patch("app.read_data", side_effect=Exception("DB error")):
        with pytest.raises(Exception, match="Failed to retrieve loans"):
            resolve_loans()

def test_add_loan_payment_valid(client):
    """Test: Making a valid payment."""
    payment_data = {
        "loan_id": 1,
        "amount": 500
    }

    response = client.post("/make_payment", json=payment_data) 

    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["loan_id"] == 1
    assert response_json["amount"] == 500
    assert response_json["payment_date"] == date.today().strftime("%Y-%m-%d")

def test_add_loan_payment_invalid(client):
    """Test: making an invalid payment by missing amount."""
    payment_data = {
        "loan_id": 1
    }

    response = client.post("/make_payment", json=payment_data)

    pytest.raises(Exception, match="Failed to add loan payment va REST")
    assert response.status_code == 500

