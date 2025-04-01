import requests

def send_otp(country: str, project_id: str, phone: str, key: str):
    """
    Sends an OTP to a phone number.
    
    :param country: The 2-letter country code (e.g., 'dz' for Algeria).
    :param project_id: The project ID for your OTP service.
    :param phone: The phone number to send the OTP to.
    :param key: The API key for authenticating the request.
    """
    url = 'https://sendotp-47lvvvrp4a-uc.a.run.app'
    headers = {
        'Content-Type': 'application/json',
        'key': key
    }
    data = {
        "country": country,
        "projectId": project_id,
        "phone": phone
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.content

def verify_otp(country: str, phone: str, project_id: str, otp: str, key: str):
    """
    Verifies an OTP for a given phone number and project ID.
    
    :param country: The 2-letter country code (e.g., 'dz' for Algeria).
    :param phone: The phone number to verify.
    :param project_id: The project ID for the OTP verification service.
    :param otp: The OTP to verify.
    :param key: The API key for authenticating the request.
    """
    url = 'https://verifyotp-47lvvvrp4a-uc.a.run.app'
    headers = {
        'Content-Type': 'application/json',
        'key': key
    }
    data = {
        "country": country,
        "phone": phone,
        "projectId": project_id,
        "otp": otp
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

