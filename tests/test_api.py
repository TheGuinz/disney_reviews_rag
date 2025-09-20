import pytest
import requests
import sys
import os

# Note: This requires the FastAPI app to be running.

BASE_URL = "http://127.0.0.1:8000"

def test_read_root():
    """
    Test the root endpoint to ensure it returns the correct welcome message.
    """
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Disneyland Review QA API. Use the /docs endpoint to see the available endpoints."}

def test_post_query():
    """
    Test the query endpoint with a valid query.
    """
    response = requests.post(f"{BASE_URL}/query", json={"query": "What are the common complaints about the food?"})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert isinstance(response.json()["answer"], str)

def test_post_query_invalid():
    """
    Test the query endpoint with an an invalid (empty) query.
    """
    response = requests.post(f"{BASE_URL}/query", json={"query": ""})
    assert response.status_code == 200
    assert "Query cannot be empty." in response.json()['answer']
    assert isinstance(response.json()["answer"], str)

def test_reset_counter_get_method():
    """
    Test the reset_counter endpoint to ensure it resets the counter.
    """
    # First, make a query to increment the counter
    requests.post(f"{BASE_URL}/query", json={"query": "Test query"})
    
    # Now, call the reset endpoint
    response = requests.get(f"{BASE_URL}/reset_counter")
    assert response.status_code == 200
    assert response.json() == {"message": "Counter has been reset to zero."}
