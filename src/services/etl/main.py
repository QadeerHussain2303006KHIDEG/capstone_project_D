from src.services.etl.transform import extract_transform
from src.services.etl.utils import (
    get_appointment,
    get_councillor,
    get_patient_councillor,
    get_rating,
)


def main() -> None:
    extract_transform(
        get_rating(), get_appointment(), get_patient_councillor(), get_councillor()
    )


if __name__ == "__main__":
    main()
