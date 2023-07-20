import json
import logging

import redis  # type:ignore
import requests  # type:ignore
from decouple import config


def get_redis(val: str) -> list[dict]:
    """
    Retrieve table data from Redis based on specialization.

    Args:
        val (str): The specialization value to filter the data.

    Returns:
        list[dict]: A list of dictionaries containing the relevant data.

    Raises:
        json.JSONDecodeError: If there is an error decoding JSON data from Redis.
        ConnectionError: If there is an issue connecting to Redis.
        TimeoutError: If a connection timeout occurs.

    Raises an exception if no data is found for the given specialization.

    """
    redis_host = config("REDIS_HOST")
    redis_port = config("REDIS_PORT")
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port)
    except (ConnectionError, TimeoutError) as e:
        logging.error(f"Connection or timeout error: {e}")
        raise
    result = None

    specialization_keys = redis_client.keys("specialization:*")
    for key in specialization_keys:
        if ((specialization := key.decode().split(":")[1])) == val and (
            (data_from_redis := redis_client.get(key)) is not None
        ):
            try:
                records = json.loads(data_from_redis)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON data: {e}")
                redis_client.close()
                raise
            top_records = records[
                :10
            ]  # data is already aggregated and sorted in descending order.
            result = [{"councillor_id": item["councillorId"]} for item in top_records]
            # `records` will contain the array of objects
            logging.info(
                f"Retrieved table data from Redis for specialization: {specialization}"
            )
            break
    redis_client.close()
    if not result:
        raise ValueError(f"{val} Data not found")
    return result


def get_report(report_id: int) -> dict:
    base_url = config("REPORT_URL")
    url = f"{base_url}/report/{report_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if not response.text:
            return {}
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred during the request: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise
