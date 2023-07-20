import unittest
from unittest import TestCase, mock

from fastapi.testclient import TestClient

from src.services.matching.matching import app


class TestAPI(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @mock.patch("src.services.matching.matching.get_report")
    @mock.patch("src.services.matching.matching.get_redis")
    def test_get_item_success(self, mock_get_redis, mock_get_report):
        mock_get_report.return_value = {
            "id": 0,
            "created": "2022-10-28T04:20:35.691Z",
            "updated": "2023-05-08T14:04:55.584Z",
            "patient_id": 5541,
            "category": "Anxiety",
            "patient_form_link": "https://watchful-supply.net/",
        }
        mock_get_redis.return_value = [{"councillor_id": "1"}, {"councillor_id": "2"}]

        response = self.client.get("/recommend/123")
        result = response.json()

        expected_result = [{"councillor_id": "1"}, {"councillor_id": "2"}]
        self.assertEqual(result, expected_result)
        mock_get_report.assert_called_once_with(123)
        mock_get_redis.assert_called_once_with("Anxiety")

    @mock.patch("src.services.matching.matching.get_report")
    @mock.patch("src.services.matching.matching.get_redis")
    def test_get_item_report_not_found(self, mock_get_redis, mock_get_report):
        mock_get_report.return_value = None

        response = self.client.get("/recommend/123")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"detail": "No data found for the specified report with ID 123"},
        )
        mock_get_redis.assert_not_called()

    @mock.patch("src.services.matching.matching.get_report")
    @mock.patch("src.services.matching.matching.get_redis")
    def test_get_item_redis_not_found(self, mock_get_redis, mock_get_report):
        mock_get_report.return_value = {"category": "example_category"}
        mock_get_redis.return_value = None

        response = self.client.get("/recommend/123")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"detail": "No data found for the specified category example_category"},
        )

        mock_get_report.assert_called_once_with(123)
        mock_get_redis.assert_called_once_with("example_category")


if __name__ == "__main__":
    unittest.main()
