import json
import unittest
from unittest.mock import MagicMock, patch

from redis.exceptions import TimeoutError
from requests.exceptions import HTTPError, RequestException

from src.services.matching.matching_utils import get_redis, get_report


class TestMatchingUtils(unittest.TestCase):
    @patch("src.services.matching.matching_utils.redis.Redis")
    @patch("src.services.matching.matching_utils.config")
    def test_get_redis_success(self, mock_config, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        specialization = "some_specialization"

        mock_records = [{"councillor_id": 1}, {"councillor_id": 2}]
        mock_client.keys.return_value = [(f"specialization:{specialization}").encode()]
        mock_client.get.return_value = '[{"councillor_id": 1}, {"councillor_id": 2}]'

        mock_config.return_value = "REDIS_VALUE"

        result = get_redis(specialization)

        self.assertEqual(result, mock_records)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.keys.assert_called_once_with("specialization:*")
        mock_client.get.assert_called_once_with(
            (f"specialization:{specialization}").encode()
        )
        mock_client.close.assert_called_once()

    @patch("src.services.matching.matching_utils.redis.Redis")
    @patch("src.services.matching.matching_utils.config")
    def test_get_redis_no_data_found(self, mock_config, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        specialization = "non_existing_specialization"

        mock_client.keys.return_value = []

        mock_config.return_value = "REDIS_VALUE"

        with self.assertRaises(ValueError) as context:
            get_redis(specialization)

        expected_error_message = f"{specialization} Data not found"
        self.assertEqual(str(context.exception), expected_error_message)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.keys.assert_called_once_with("specialization:*")
        mock_client.close.assert_called_once()

    @patch("src.services.matching.matching_utils.redis.Redis")
    @patch("src.services.matching.matching_utils.config")
    def test_get_redis_connection_error(self, mock_config, mock_redis):
        mock_redis.side_effect = ConnectionError("Connection error occurred")

        specialization = "some_specialization"

        mock_config.return_value = "REDIS_VALUE"

        with self.assertRaises(ConnectionError) as context:
            get_redis(specialization)

        expected_error_message = "Connection error occurred"
        self.assertEqual(str(context.exception), expected_error_message)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")

    @patch("src.services.matching.matching_utils.redis.Redis")
    @patch("src.services.matching.matching_utils.config")
    def test_get_redis_timeout_error(self, mock_config, mock_redis):
        mock_redis.side_effect = TimeoutError("Timeout error occurred")

        specialization = "some_specialization"

        mock_config.return_value = "REDIS_VALUE"

        with self.assertRaises(TimeoutError) as context:
            get_redis(specialization)

        expected_error_message = "Timeout error occurred"
        self.assertEqual(expected_error_message, str(context.exception))

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")

    @patch("src.services.matching.matching_utils.redis.Redis")
    @patch("src.services.matching.matching_utils.config")
    def test_get_redis_json_decode_error(self, mock_config, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        specialization = "some_specialization"

        mock_client.keys.return_value = [f"specialization:{specialization}".encode()]
        mock_client.get.return_value = "invalid_json_data"

        mock_config.return_value = "REDIS_VALUE"

        with self.assertRaises(json.JSONDecodeError):
            get_redis(specialization)

        mock_redis.assert_called_once_with(host="REDIS_VALUE", port="REDIS_VALUE")
        mock_client.keys.assert_called_once_with("specialization:*")
        mock_client.get.assert_called_once_with(
            (f"specialization:{specialization}").encode()
        )
        mock_client.close.assert_called_once()

    @patch("src.services.matching.matching_utils.config")
    @patch("src.services.matching.matching_utils.requests.get")
    def test_get_report_success(self, mock_get, mock_config):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 0,
            "created": "2022-10-28T04:20:35.691Z",
            "updated": "2023-05-08T14:04:55.584Z",
            "patient_id": 5541,
            "category": "Anxiety",
            "patient_form_link": "https://watchful-supply.net/",
        }
        mock_get.return_value = mock_response

        mock_config.return_value = "http://test.com"

        result = get_report(123)

        self.assertEqual(result, mock_response.json.return_value)

        mock_get.assert_called_once_with("http://test.com/report/123")

    @patch("src.services.matching.matching_utils.config")
    @patch("src.services.matching.matching_utils.requests.get")
    def test_get_report_http_error(self, mock_get, mock_config):
        mock_get.side_effect = HTTPError("404 Not Found")

        mock_config.return_value = "http://test.com"

        with self.assertRaises(HTTPError):
            get_report(123)

        mock_get.assert_called_once_with("http://test.com/report/123")

    @patch("src.services.matching.matching_utils.config")
    @patch("src.services.matching.matching_utils.requests.get")
    def test_get_report_request_exception(self, mock_get, mock_config):
        mock_get.side_effect = RequestException("Connection error")

        mock_config.return_value = "http://test.com"

        with self.assertRaises(RequestException):
            get_report(123)

        mock_get.assert_called_once_with("http://test.com/report/123")

    @patch("src.services.matching.matching_utils.config")
    @patch("src.services.matching.matching_utils.requests.get")
    def test_get_report_empty_response(self, mock_get, mock_config):
        mock_response = MagicMock()
        mock_response.text = ""
        mock_get.return_value = mock_response

        mock_config.return_value = "http://test.com"

        result = get_report(123)

        self.assertEqual(result, {})

        mock_get.assert_called_once_with("http://test.com/report/123")


if __name__ == "__main__":
    unittest.main()
