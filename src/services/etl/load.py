import json
import logging
from typing import List

import redis  # type: ignore
from decouple import config
from pyspark.sql import DataFrame
from redis.exceptions import RedisError  # type: ignore


def load_in_redis(specializations: List[str], grouped_df: DataFrame) -> None:
    """
    Load data into Redis for each specialization.

    Args:
        specializations (List[str]): List of specialization names.
        grouped_df (DataFrame): Spark DataFrame containing grouped data.

    Returns:
        None
    """

    logging.basicConfig(level=logging.DEBUG)

    try:
        redis_host = config("REDIS_HOST")
        redis_port = config("REDIS_PORT")
        redis_client = redis.Redis(host=redis_host, port=redis_port)
    except RedisError as e:
        logging.error(f"Failed to connect to Redis: {str(e)}")
        raise

    try:
        for specialization in specializations:
            specialization_table = grouped_df.filter(
                grouped_df.specialization == specialization
            )
            strip_data = specialization_table.select("councillorId", "points")

            records = strip_data.toPandas().to_json(orient="records")
            records = json.dumps(json.loads(records))

            redis_key = f"specialization:{specialization}"
            redis_client.set(redis_key, records)
            logging.info(
                f"Stored table data in Redis for specialization {specialization}"
            )

    except RedisError as e:
        logging.error(f"Redis error occurred while loading data: {str(e)}")
        redis_client.close()
        raise

    redis_client.close()
