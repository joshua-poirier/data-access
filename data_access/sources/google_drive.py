# pylint: disable=no-member

import io
import logging
from datetime import datetime
from typing import (
    Any,
    Dict,
    Optional,
)

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

from .config import GoogleDriveServiceAccountInfo

logger = logging.getLogger()


class GoogleDriveClient:
    """Client for interacting with Google Drive API.

    This client is intended to be used to interact with Google Drive
    files. It is assumed that the files are shared with the Service
    Account email. The client can retrieve the File ID for a given
    filename, download the file to disk, and read the file into a
    pandas DataFrame.

    Attributes:
        api_name (str): The name of the API.
        api_version (str): The version of the API.
        scopes (List[str]): The scopes required to access the API.
        file_id (str): The Google Drive File ID.
        io_options (Dict[str, Any]): Options for reading the file into a
            DataFrame.
        client (Resource): The Google Drive API
    """

    api_name: str = "drive"
    api_version: str = "v3"
    scopes = ["https://www.googleapis.com/auth/drive"]

    def __init__(
        self,
        file_id: Optional[str] = None,
        io_options: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.file_id: Optional[str] = file_id
        self.io_options: Dict[str, Any] = io_options or {}
        self.client: Resource = GoogleDriveClient.connect()

    @property
    def source_created_at(self) -> Optional[str]:
        """When the file was created in Google Drive.

        Returns:
            datetime: Datetime for when the data source file was created.
        """
        return str(
            self.client.files()
            .get(fileId=self.file_id, fields="createdTime")
            .execute()
            .get("createdTime")
        )

    @property
    def source_updated_at(self) -> Optional[str]:
        """When the file was updated in Google Drive.

        Returns:
            datetime: Datetime for when the data source file was updated.
        """
        return str(
            self.client.files()
            .get(fileId=self.file_id, fields="modifiedTime")
            .execute()
            .get("modifiedTime")
        )

    @property
    def source_filename(self) -> Optional[str]:
        """Filename of the source in Google Drive.

        Returns:
            str: Name of the file in Google Drive.
        """
        return str(self.client.files().get(fileId=self.file_id).execute().get("name"))

    @property
    def source_uri(self) -> Optional[str]:
        """URI to view the file in Google Drive.

        Returns:
            str: URI to view the file in Google Drive.
        """
        return str(
            self.client.files()
            .get(fileId=self.file_id, fields="webViewLink")
            .execute()
            .get("webViewLink")
        )

    @staticmethod
    def connect() -> Resource:
        """Create a client that communicates to a Google API.

        Args:
            key_file_location: The path to a valid service account JSON
            key file.
        """
        credentials = service_account.Credentials.from_service_account_info(
            info=GoogleDriveServiceAccountInfo().model_dump()  # type: ignore
        )
        scoped_credentials = credentials.with_scopes(GoogleDriveClient.scopes)

        client = build(
            GoogleDriveClient.api_name,
            GoogleDriveClient.api_version,
            credentials=scoped_credentials,
        )
        logger.info("Google Drive API client connected")

        return client

    def get_file_id(self, filename: str) -> None:
        """Retrieves the Google Drive File ID for a given filename.

        Client only has access to files which have been shared with the
        Service Account. At the time of this writing, this will not be a
        large number of files. It is important to remember to share any
        updated files with the Service Account email. Otherwise the
        program will not have access to the file.

        The retrieved File ID is then stored in the client object's
        `file_id` attribute.

        Args:
            filename (str): Name of the file (without path) to look for.

        Raises:
            ValueError: No files are found in Google Drive.
            ValueError: `filename` could not be found in Google Drive.
        """
        results = self.client.files().list(fields="files(id, name)").execute()
        items = results.get("files", [])

        if not items:
            logger.error("No files found, ensure access shared with service account.")
            raise ValueError("No files found")
        for item in items:
            if item.get("name", "") == filename:
                logger.info(f"Found '{filename}' in Google Drive")
                self.file_id = item.get("id")
                return

        logger.error(f"Could not find {filename} in Google Drive")
        raise ValueError(f"Could not find file '{filename}'")

    def download(self) -> None:
        """Downloads a given file to local disk."""
        # retrieve the filename
        filename = self.client.files().get(fileId=self.file_id).execute().get("name")

        # write the stream to disk
        stream = self._stream()
        with io.open(filename, "wb") as f:
            stream.seek(0)
            f.write(stream.read())

        logger.info(f"'{filename}' downloaded successfully")

    def _stream(self) -> io.BytesIO:
        """Create a data stream.

        Returns:
            io.BytesIO: Google Drive data as a bytes stream.
        """
        if self.file_id is None:
            raise ValueError("No file_id set. Use `get_file_id` to set.")

        # setup the download stream
        request = self.client.files().get_media(fileId=self.file_id)
        stream = io.BytesIO()
        downloader = MediaIoBaseDownload(stream, request)
        done = False
        pbar = tqdm(total=100, ncols=70)

        # download the stream
        while not done:
            status, done = downloader.next_chunk()
            if status:
                pbar.update(int(status.progress() * 100) - pbar.n)
        pbar.close()

        return stream

    def read(self) -> pd.DataFrame:
        """Read the bytes stream into a dataframe.

        Assumes data is an Excel file.

        Returns:
            pd.DataFrame: Google Drive sourced data as a dataframe.
        """
        logger.info("Reading data from Google Drive into dataframe")
        stream: io.BytesIO = self._stream()
        stream.seek(0)
        return pd.read_csv(stream, **self.io_options)
