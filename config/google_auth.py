"""Módulo de autenticación con Google OAuth2."""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config.settings import GOOGLE_SCOPES

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")


def get_google_credentials() -> Credentials:
    """Obtiene credenciales válidas de Google, renovando si es necesario."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def build_service(service_name: str, version: str):
    """Construye un servicio de Google API autenticado."""
    from googleapiclient.discovery import build

    creds = get_google_credentials()
    return build(service_name, version, credentials=creds)
