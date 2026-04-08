"""Automatización de Google Sheets: leer, escribir, reportes."""

from config.google_auth import build_service


class SheetsAutomation:
    def __init__(self):
        self.service = build_service("sheets", "v4")

    def read_sheet(self, spreadsheet_id: str, range_name: str) -> list[list]:
        """Lee datos de una hoja de cálculo."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()

        return result.get("values", [])

    def write_to_sheet(
        self, spreadsheet_id: str, range_name: str, values: list[list]
    ) -> dict:
        """Escribe datos en una hoja de cálculo."""
        body = {"values": values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        return {
            "updated_cells": result.get("updatedCells", 0),
            "updated_range": result.get("updatedRange", ""),
        }

    def append_to_sheet(
        self, spreadsheet_id: str, range_name: str, values: list[list]
    ) -> dict:
        """Agrega filas al final de una hoja."""
        body = {"values": values}
        result = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

        return {
            "updated_cells": result.get("updates", {}).get("updatedCells", 0),
            "updated_range": result.get("updates", {}).get("updatedRange", ""),
        }

    def create_spreadsheet(self, title: str) -> dict:
        """Crea una nueva hoja de cálculo."""
        spreadsheet = {"properties": {"title": title}}
        result = self.service.spreadsheets().create(
            body=spreadsheet, fields="spreadsheetId,spreadsheetUrl"
        ).execute()

        return {
            "id": result["spreadsheetId"],
            "url": result["spreadsheetUrl"],
        }
