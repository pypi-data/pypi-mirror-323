import requests

def make_request(method, url, data=None, headers=None):
    """Handles making HTTP requests."""
    try:
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'GET':
            response = requests.get(url, params=data, headers=headers)
        else:
            raise ValueError("Invalid HTTP method")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HTTP request failed: {str(e)}")
