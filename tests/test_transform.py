import unittest

from src.services.etl.transform import extract_transform


class ExtractTransformTestCase(unittest.TestCase):
    def test_extract_transform(self):
        rating = [
            {"id": 0, "appointment_id": 1358, "value": 5},
            {"id": 1, "appointment_id": 6086, "value": 2},
            {"id": 2, "appointment_id": 4734, "value": 3},
        ]
        appointment = [
            {"id": 0, "patient_id": 5532},
            {"id": 1, "patient_id": 754},
            {"id": 2, "patient_id": 9900},
        ]
        patient_councillor = [
            {"id": 0, "patient_id": 6591, "councillor_id": 3751},
            {"id": 1, "patient_id": 1668, "councillor_id": 3482},
            {"id": 2, "patient_id": 4731, "councillor_id": 7866},
        ]
        councillor = [
            {"id": 0, "specialization": "Anxiety", "user_id": 0},
            {"id": 1, "specialization": "Depression", "user_id": 1},
            {"id": 2, "specialization": "Anxiety", "user_id": 2},
        ]

        result_df = extract_transform(
            rating, appointment, patient_councillor, councillor
        )

        expected_columns = ["councillor_id", "specialization", "points"]
        self.assertListEqual(result_df.columns, expected_columns)

    def test_extract_transform_with_invalid_data(self):
        rating = {"id": [1, 2, 3], "appointment_id": [1, 2, 3], "value": [5, 4, 3]}
        appointment = {"id": [1, 2, 3], "patient_id": [1, 2, 3]}

        patient_councillor = {"patient_id": [1, 2, 3], "councillor_id": [1, 2, 3]}
        councillor = {
            "id": [1, 2, 3],
            "specialization": ["therapy", "counselling", "therapy"],
        }

        with self.assertRaises(TypeError):
            extract_transform(rating, appointment, patient_councillor, councillor)


if __name__ == "__main__":
    unittest.main()
