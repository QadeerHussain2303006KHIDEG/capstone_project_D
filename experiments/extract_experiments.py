import time

import requests  # type: ignore
from decouple import config

# solution proposed by arshad shiwani
# This code is just for experimenting with certain ideas such as response time, regarding the task it is by no means the final production code.

base_url = config("BASE_URL")


def get_rating():
    start_time = time.time()

    url = f"{base_url}/rating"

    response = requests.get(url)
    end_time = time.time()

    if response.status_code == 200:
        print("getting response")
        data = response.json()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time} seconds")
        return data
    else:
        return "no response"  # just added here to see the response error handling was not in scope of this experiment


def get_appointment():
    start_time = time.time()

    url = f"{base_url}/appointment"

    response = requests.get(url)
    end_time = time.time()

    if response.status_code == 200:
        print("getting response")
        data = response.json()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time} seconds")
        return data
    else:
        return "no response"  # just added here to see the response error handling was not in scope of this experiment


def get_patient_councillor():
    start_time = time.time()

    url = f"{base_url}/patient_councillor"

    response = requests.get(url)
    end_time = time.time()

    if response.status_code == 200:
        print("getting response")
        data = response.json()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time} seconds")
        return data
    else:
        return "no response"  # just added here to see the response error handling was not in scope of this experiment


def get_councillor():
    start_time = time.time()

    url = f"{base_url}/councillor"

    response = requests.get(url)
    end_time = time.time()

    if response.status_code == 200:
        print("getting response")
        data = response.json()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time} seconds")
        return data
    else:
        return "no response"  # just added here to see the response error handling was not in scope of this experiment
