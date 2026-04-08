"""Automatización de Google Drive: listar, buscar archivos."""

from config.google_auth import build_service


class DriveAutomation:
    def __init__(self):
        self.service = build_service("drive", "v3")

    def list_recent_files(self, max_results: int = 10) -> list[dict]:
        """Lista los archivos más recientes."""
        results = self.service.files().list(
            pageSize=max_results,
            orderBy="modifiedTime desc",
            fields="files(id, name, mimeType, modifiedTime, webViewLink, owners)",
        ).execute()

        return [
            {
                "id": f["id"],
                "name": f["name"],
                "type": f["mimeType"],
                "modified": f["modifiedTime"],
                "link": f.get("webViewLink", ""),
                "owner": f.get("owners", [{}])[0].get("displayName", ""),
            }
            for f in results.get("files", [])
        ]

    def search_files(self, query: str, max_results: int = 10) -> list[dict]:
        """Busca archivos por nombre o contenido."""
        results = self.service.files().list(
            q=f"name contains '{query}' or fullText contains '{query}'",
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        ).execute()

        return [
            {
                "id": f["id"],
                "name": f["name"],
                "type": f["mimeType"],
                "modified": f["modifiedTime"],
                "link": f.get("webViewLink", ""),
            }
            for f in results.get("files", [])
        ]

    def get_storage_info(self) -> dict:
        """Obtiene información del almacenamiento."""
        about = self.service.about().get(
            fields="storageQuota"
        ).execute()

        quota = about["storageQuota"]
        used = int(quota.get("usage", 0))
        limit = int(quota.get("limit", 0))

        return {
            "used_gb": round(used / (1024**3), 2),
            "limit_gb": round(limit / (1024**3), 2) if limit else "Unlimited",
            "percent_used": round((used / limit) * 100, 1) if limit else 0,
        }
