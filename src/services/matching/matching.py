import logging
from typing import Dict, List

import requests  # type:ignore
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from src.services.matching.matching_utils import get_redis, get_report

app = FastAPI()


@app.get("/recommend/{report_id}")
def get_item(report_id: int) -> List[Dict[str, str]]:
    """
    Get item endpoint to process GET requests.

    Args:
        report_id: An int representing the report id received in the API endpoint.

    Raises:
        HTTPException: If there are errors during data retrieval.

    Returns:
        List[Dict[str, str]]: The retrieved data.

    """
    try:
        if not (report := get_report(report_id)):
            raise HTTPException(
                status_code=404,
                detail=f"No data found for the specified report with ID {report_id}",
            )

        category = report["data"]["category"]
        if not (result := get_redis(category)):
            raise HTTPException(
                status_code=404,
                detail=f"No data found for the specified category {category}",
            )
        return result

    except requests.exceptions.RequestException as req_exc:
        logging.error(f"Request error occurred: {req_exc}")
        raise HTTPException(status_code=500, detail=str(req_exc)) from req_exc


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
