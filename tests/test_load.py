import unittest
from unittest.mock import MagicMock, patch

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType
from redis import RedisError

from src.services.etl.load import load_in_redis


class LoadMockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Spark session
        cls.spark = SparkSession.builder.getOrCreate()
        # Create the sample DataFrame
        schema = StructType(
            [
                StructField("councillor_id", IntegerType(), nullable=False),
                StructField("specialization", StringType(), nullable=False),
                StructField("points", IntegerType(), nullable=False),
            ]
        )
        sample_data = [
            {"councillor_id": 2243, "specialization": "bipolar", "points": 2},
            {"councillor_id": 2243, "specialization": "bipolar", "points": 2},
            {"councillor_id": 2243, "specialization": "bipolar", "points": 2},
            {"councillor_id": 2243, "specialization": "bipolar", "points": 2},
            {"councillor_id": 2243, "specialization": "stress", "points": 2},
            {"councillor_id": 2243, "specialization": "stress", "points": 2},
            {"councillor_id": 2243, "specialization": "stress", "points": 2},
        ]
        cls.sample_df = cls.spark.createDataFrame(sample_data, schema)

    @classmethod
    def tearDownClass(cls):
        # Stop the Spark session
        cls.spark.stop()

    @patch("src.services.etl.load.redis.Redis", autospec=True)
    @patch("src.services.etl.load.config")
    def test_load_in_redis(self, mock_config, mock_redis):
        mock_client = MagicMock()

        mock_redis.return_value = mock_client

        mock_config.return_value = "REDIS_VALUE"

        mock_load_in_redis = MagicMock()
        mock_load_in_redis.side_effect = (
            lambda specializations, df: self._mock_load_in_redis(
                specializations, df, mock_client
            )
        )

        with patch("src.services.etl.load.load_in_redis", mock_load_in_redis):
            load_in_redis(["bipolar", "stress"], self.sample_df)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.set.assert_called()

    def _mock_load_in_redis(self, specializations, df, redis_client):
        expected_specializations = set(specializations)
        actual_specializations = set(
            df.select("specialization").distinct().rdd.flatMap(lambda x: x).collect()
        )
        self.assertEqual(expected_specializations, actual_specializations)

        expected_redis_calls = len(expected_specializations)
        actual_redis_calls = redis_client.set.call_count
        self.assertEqual(expected_redis_calls, actual_redis_calls)

    @patch("src.services.etl.load.redis.Redis")
    @patch("src.services.etl.load.config")
    def test_load_in_redis_empty_df(self, mock_config, mock_redis):
        mock_client = MagicMock()

        mock_redis.return_value = mock_client

        mock_config.return_value = "REDIS_VALUE"

        grouped_df = self.sample_df.filter(
            "1=0"
        )  # empties the dataset while maintaining the schema

        mock_load_in_redis = MagicMock()
        mock_load_in_redis.side_effect = (
            lambda specializations, df: self._mock_load_in_redis(
                specializations, df, mock_client
            )
        )

        with patch("src.services.etl.load.load_in_redis", mock_load_in_redis):
            load_in_redis(["bipolar", "stress"], grouped_df)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.set.assert_called()

    @patch("src.services.etl.load.redis.Redis", autospec=True)
    @patch("src.services.etl.load.config")
    def test_load_in_redis_redis_client_failure(self, mock_config, mock_redis):
        mock_config.return_value = "REDIS_VALUE"

        mock_redis.side_effect = RedisError("Failed to connect to Redis")

        with self.assertRaises(RedisError) as context:
            load_in_redis(["bipolar"], self.sample_df)

        self.assertIsInstance(context.exception, RedisError)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")

    @patch("src.services.etl.load.redis.Redis")
    @patch("src.services.etl.load.config")
    def test_load_in_redis_redis_error(self, mock_config, mock_redis):
        mock_config.return_value = "REDIS_VALUE"

        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        mock_client.set.side_effect = RedisError(
            "Redis error occurred while loading data"
        )

        with self.assertRaises(RedisError) as context:
            load_in_redis(["bipolar"], self.sample_df)

        self.assertIsInstance(context.exception, RedisError)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.set.assert_called()


if __name__ == "__main__":
    unittest.main()
