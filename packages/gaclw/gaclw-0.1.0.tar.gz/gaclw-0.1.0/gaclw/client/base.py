"""Base class for clients"""

import logging
import sys
from pathlib import Path

from google.auth.external_account_authorized_user import (
    Credentials as ExternalAccountCredentials,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from gaclw.core.config import settings


class GoogleApiClient(object):
    """Base class for clients"""

    # https://developers.google.com/drive/api/guides/api-specific-auth
    # https://developers.google.com/sheets/api/scopes?hl=ja
    TOKEN_FILE_PATH = Path(settings.SECRET_FOLDER, "token.json")
    CREDENTIALS_FILE_PATH = Path(settings.SECRET_FOLDER, "credentials.json")

    def __init__(
        self,
        service_name: str,
        version: str,
        scopes: list[str],
        log_level: int = 2,
    ):
        self._logger = self.get_logger(log_level)
        self._credentials = self.authenticate(scopes)
        self._service = build(service_name, version, credentials=self._credentials)

    @property
    def logger(self) -> logging.Logger:
        """_summary_

        Returns:
            logging.Logger: _description_
        """
        return self._logger

    @property
    def service(self) -> Resource:
        """_summary_

        Returns:
            Resource: _description_
        """
        return self._service

    @classmethod
    def get_logger(cls, level: int = 2) -> logging.Logger:
        """_summary_

        Args:
            level (int, optional): _description_. Defaults to 2.

        Returns:
            logging.Logger: _description_
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(level * 10)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt=r"%Y-%m-%dT%H:%M:%S%z",
        )
        # ログを標準出力する
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @classmethod
    def authenticate(cls, scopes: list[str]) -> Credentials | ExternalAccountCredentials:
        """_summary_

        Args:
            scopes (list[str]): _description_

        Returns:
            Credentials | ExternalAccountCredentials: _description_
        """
        credentials = None
        if cls.TOKEN_FILE_PATH.exists():
            credentials = Credentials.from_authorized_user_file(
                cls.TOKEN_FILE_PATH, scopes
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cls.CREDENTIALS_FILE_PATH, scopes
                )
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(cls.TOKEN_FILE_PATH, "w", encoding="utf-8") as token:
                token.write(credentials.to_json())
        return credentials
