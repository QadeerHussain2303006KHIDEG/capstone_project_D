import logging
import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import avg, desc, explode, split
from pyspark.sql.types import IntegerType, StringType, StructField, StructType
from redis.exceptions import RedisError  # type: ignore

from src.services.etl.load import load_in_redis


def extract_transform(
    rating: DataFrame,
    appointment: DataFrame,
    patient_councillor: DataFrame,
    councillor: DataFrame,
) -> DataFrame:
    """
    Extracts data from different sources, performs transformation, and loads the transformed data into Redis.

    Args:
        rating (DataFrame): DataFrame containing Rating objects.
        appointment (DataFrame): DataFrame containing Appointment objects.
        patient_councillor (DataFrame): DataFrame containing PatientCouncillor objects.
        councillor (DataFrame): DataFrame containing Councillor objects.

    Returns:
        DataFrame: The transformed DataFrame if data is loaded successfully into Redis.
    """

    spark = SparkSession.builder.getOrCreate()
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    counselor_schema = StructType(
        [
            StructField("id", IntegerType(), nullable=False),
            StructField("userId", IntegerType(), nullable=False),
            StructField("specialization", StringType(), nullable=True),
            StructField("description", StringType(), nullable=True),
        ]
    )

    rating = spark.createDataFrame(rating)
    appointment = spark.createDataFrame(appointment)
    patient_councillor = spark.createDataFrame(patient_councillor)

    councillor = spark.createDataFrame(councillor, counselor_schema)
    logging.info("Data Fetched from API's")

    joined_df = (
        rating.join(appointment, rating["appointmentId"] == appointment["id"])
        .join(
            patient_councillor,
            patient_councillor["patientId"] == appointment["patientId"],
        )
        .join(councillor, councillor["id"] == patient_councillor["councillorId"])
    )

    exploded_df = joined_df.withColumn(
        "specialization", explode(split(joined_df["specialization"], ","))
    )

    grouped_df = (
        exploded_df.groupBy("councillorId", "specialization")
        .agg(avg("value").alias("points"))
        .orderBy(desc("points"))
    )

    specializations = (
        grouped_df.select("specialization")
        .distinct()
        .toPandas()["specialization"]
        .tolist()
    )
    logging.info("Data Transformed Successfully")

    try:
        load_in_redis(specializations, grouped_df)
        logging.info(f"Data Loaded in Redis successfully with keys {specializations}")
    except RedisError as e:
        logging.error(f"Redis error occurred during data loading: {str(e)}")
        spark.stop()
        raise

    spark.stop()
    return grouped_df
