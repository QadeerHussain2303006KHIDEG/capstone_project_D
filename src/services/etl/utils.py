import logging

import requests  # type: ignore
from decouple import config

base_url = config("BASE_URL")

rating_url = config("RATING_URL")
appointment_url = config("APPOINTMENT_URL")
patient_councillor_url = config("PATIENT_COUNCILLOR_URL")
councillor_url = config("COUNCILLOR_URL")


def url_request_handler(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx response codes
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred during the request: {e}")
        raise
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        raise


def get_rating() -> dict:
    url = f"{rating_url}/rating"
    return url_request_handler(url)


def get_appointment() -> dict:
    url = f"{appointment_url}/appointments"
    return url_request_handler(url)


def get_patient_councillor() -> dict:
    url = f"{patient_councillor_url}/patient_councillor"
    return url_request_handler(url)


def get_councillor() -> dict:
    url = f"{councillor_url}/counselor"
    return url_request_handler(url)
