# OTP Service

A Python package to send and verify OTPs using Smssak service.

## Installation

```bash
pip install smssak
```

## Usage

```python
from smssak.otp import send_otp, verify_otp

# Send OTP
response = send_otp('country_code', 'project_id', 'phone_number', 'api_key')
print(response)

# Verify OTP
response = verify_otp('country_code','phone_number','project_id',"code",'api_key'))
print(response)
```
