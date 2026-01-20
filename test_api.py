import requests
import json

# Base URL - change this to your deployed URL
BASE_URL = "http://localhost:5000"

def test_home():
    """Test the home endpoint"""
    print("Testing GET / ...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_health():
    """Test the health check endpoint"""
    print("Testing GET /health ...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_prediction():
    """Test the prediction endpoint"""
    print("Testing POST /predict ...")

    # Test cases
    test_cases = [
        {
            "name": "Small house",
            "data": {"bedrooms": 2, "bathrooms": 1, "sqft": 1000, "age": 20}
        },
        {
            "name": "Medium house",
            "data": {"bedrooms": 3, "bathrooms": 2, "sqft": 2000, "age": 10}
        },
        {
            "name": "Large house",
            "data": {"bedrooms": 5, "bathrooms": 3, "sqft": 4000, "age": 5}
        }
    ]

    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Input: {test_case['data']}")

        response = requests.post(
            f"{BASE_URL}/predict",
            json=test_case['data'],
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 50)
    print("House Price Prediction API Test Suite")
    print("=" * 50 + "\n")

    try:
        test_home()
        test_health()
        test_prediction()

        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the API is running at", BASE_URL)
    except Exception as e:
        print(f"\nError: {e}")
