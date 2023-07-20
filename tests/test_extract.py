import unittest
from unittest.mock import patch

import requests  # type: ignore

from src.services.etl.utils import url_request_handler


class ExtractTest(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://xloop-dummy.herokuapp.com"

    @patch("requests.get")
    def test_url_request_handler_http_error(self, mock_get):
        urls = [
            f"{self.base_url}/rating",
            f"{self.base_url}/councillor",
            f"{self.base_url}/patient_councillor",
            f"{self.base_url}/appointment",
        ]
        mock_response = requests.HTTPError("404 Client Error")
        mock_get.return_value.raise_for_status.side_effect = mock_response

        for url in urls:
            with self.assertRaises(requests.HTTPError):
                url_request_handler(url)

            mock_get.assert_called_once_with(url)
            mock_get.return_value.raise_for_status.assert_called_once()
            mock_get.reset_mock()

    @patch("requests.get")
    def test_url_request_handler_json_decode_error(self, mock_get):
        urls = [
            f"{self.base_url}/rating",
            f"{self.base_url}/councillor",
            f"{self.base_url}/patient_councillor",
            f"{self.base_url}/appointment",
        ]
        mock_response = requests.JSONDecodeError("Error decoding JSON response", "", 0)
        mock_get.return_value.json.side_effect = mock_response

        for url in urls:
            with self.assertRaises(requests.JSONDecodeError):
                url_request_handler(url)

            mock_get.assert_called_once_with(url)
            mock_get.return_value.json.assert_called_once()
            mock_get.reset_mock()

    @patch("requests.get")
    def test_url_request_handler_request_exception(self, mock_get):
        urls = [
            f"{self.base_url}/rating",
            f"{self.base_url}/councillor",
            f"{self.base_url}/patient_councillor",
            f"{self.base_url}/appointment",
        ]
        request_exception = requests.RequestException(
            "Error occurred during the request"
        )
        mock_get.side_effect = request_exception

        for url in urls:
            with self.assertRaises(requests.RequestException):
                url_request_handler(url)

            mock_get.assert_called_once_with(url)
            mock_get.reset_mock()


if __name__ == "__main__":
    unittest.main()
