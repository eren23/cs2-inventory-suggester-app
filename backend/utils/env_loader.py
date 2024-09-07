import os
from dotenv import load_dotenv


def load_environment_variables():
    load_dotenv()
    hf_token = os.getenv("HF_AUTH_TOKEN")
    print("hf_token", hf_token)
    return hf_token
