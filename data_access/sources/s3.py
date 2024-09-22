import logging
from typing import (
    Any,
    Dict,
    Optional,
)

import boto3
import pandas as pd

from .config import AWSSession

logger = logging.getLogger()

class S3Client:
    """Client for interacting with the S3 API.

    This client is intended to be used to interact with S3 files.
    """

    def __init__(self, io_options: Optional[Dict[str, Any]] = None) -> None:
        self.io_options: Dict[str, Any] = io_options or {}
        self.client = S3Client.connect()

    @staticmethod
    def connect():
        session = boto3.Session(**AWSSession().model_dump())
        logger.info("Connected to AWS.")

        return session.client("s3")

    def write(
        self, df: pd.DataFrame, bucket: str, filename: str
    ) -> None:
        csv_buffer = df.to_csv(**self.io_options)

        logger.info("Writing dataframe to S3.")
        self.client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=csv_buffer,
        )
