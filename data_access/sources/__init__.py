import logging
from abc import ABC, abstractmethod

import pandas as pd
from pydantic import BaseModel

logger = logging.getLogger()


class DataSource(ABC, BaseModel):
    """Superclass for all Data Sources."""

    @property
    @abstractmethod
    def source_created_at(self) -> str:
        """Datetime when the source was created.

        Returns:
            datetime: Datetime when the source was created.
        """

    @property
    @abstractmethod
    def source_updated_at(self) -> str:
        """Datetime when the source was last updated.

        Returns:
            datetime: Datetime when the source was last updated.
        """

    @property
    @abstractmethod
    def source_filename(self) -> str:
        """Filename of the source.

        Returns:
            str: Filename of the source.
        """

    @property
    @abstractmethod
    def source_uri(self) -> str:
        """URI of the source.

        Returns:
            str: URI of the source.
        """

    @property
    def source_ingest_configuration(self) -> str:
        """Ingest configuration of the source.

        Returns:
            str: Ingest configuration of the source.
        """
        return self.model_dump_json()

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Read the data from the source.

        Returns:
            pd.DataFrame: Data read from the source.
        """
