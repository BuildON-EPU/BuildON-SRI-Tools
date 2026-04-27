from requests import post

def get_fastapi_token():
    # Credentials for authentication
    auth_data = {'email': 'jpapias@epu.ntua.gr', 'password': 'jpjpjp'}

    # 1. Authenticate with FastAPI to get the token
    try:
        login_response = post('http://localhost:3000/token', json=auth_data)

        # Check if authentication was successful
        if login_response.status_code == 200:
            # Retrieve and return the token
            token = login_response.json().get("access_token")
            print(f"Token received: {token}")
            return token
        else:
            print(f"Error during authentication: {login_response.status_code}")
            return None

    except Exception as e:
        print(f"Exception during token request: {e}")
        return None

# Example usage
token = get_fastapi_token()
if token:
    print(f"Successfully retrieved token: {token}")
else:
    print("Failed to retrieve token.")
