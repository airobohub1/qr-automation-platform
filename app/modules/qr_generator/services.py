import os
import os, requests
from dotenv import load_dotenv

load_dotenv()
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")

# def validate_session(cookies):
#     return requests.get(
#         "/api/validate-session",
#         cookies=cookies,
#         timeout=5
#     )


def validate_session(cookies):
    return requests.get(
        f"{FASTAPI_BASE_URL}/api/validate-session",
        cookies=cookies,
        timeout=5
    )

def get_usage(user_id):
    return requests.get(f"{FASTAPI_BASE_URL}/api/usage/{user_id}")
    # return requests.get("/api/usage/{user_id}")


def get_profile(user_id):
    return requests.get(f"{FASTAPI_BASE_URL}/api/profile/{user_id}")
    # return requests.get("/api/profile/{user_id}")

def update_profile(user_id, data):
    return requests.post(f"{FASTAPI_BASE_URL}/api/profile/{user_id}", data=data)
    # return requests.post("/api/profile/{user_id}", data=data)


def submit_lead(data):
    return requests.post(f"{FASTAPI_BASE_URL}/api/lead", data=data)
    # return requests.post("/api/lead", data=data)

