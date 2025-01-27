from typing import Any

from googleapiclient.errors import HttpError

from gaclw.client.base import GoogleApiClient


class GoogleSpreadsheetsApiClient(GoogleApiClient):
    def __init__(self, log_level: int = 2):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        super().__init__("sheets", "v4", scopes, log_level)
        self._spreadsheets = self.service.spreadsheets()  # type: ignore

    @property
    def spreadsheets(self):
        return self._spreadsheets

    def append_values(
        self, spreadsheet_id: str, range_name: str, values: list[list[Any]]
    ) -> None:
        try:
            result = (
                self.spreadsheets.values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    body={"values": values},
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                )
                .execute()
            )
            self.logger.info(
                f"Updated Range: {result.get('updates').get('updatedRange')}"
            )
            self.logger.info(f"Updated Rows: {result.get('updates').get('updatedRows')}")
            self.logger.info(
                f"Updated Columns: {result.get('updates').get('updatedColumns')}"
            )
            self.logger.info(
                f"Updated Cells: {result.get('updates').get('updatedCells')}"
            )
        except HttpError as err:
            self.logger.error(err)
            return None

    def get_values(self, spreadsheet_id: str, range_name: str) -> list[list[Any]] | None:
        try:
            result = (
                self.spreadsheets.values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                )
                .execute()
            )
            self.logger.info(f"Major dimension: {result.get('majorDimension')}")
            self.logger.info(f"Range: {result.get('range')}")
            return result.get("values")
        except HttpError as err:
            self.logger.error(err)
            return None
