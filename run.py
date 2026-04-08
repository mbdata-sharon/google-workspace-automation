"""Punto de entrada principal - Inicia el dashboard y/o el bot."""

import sys
import uvicorn
from config.settings import APP_PORT


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python run.py dashboard   - Inicia el dashboard web")
        print("  python run.py bot         - Inicia el bot de Telegram")
        print("  python run.py all         - Inicia ambos")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "dashboard":
        print(f"Iniciando dashboard en http://localhost:{APP_PORT}")
        uvicorn.run("backend.app.main:app", host="0.0.0.0", port=APP_PORT, reload=True)

    elif mode == "bot":
        print("Iniciando bot de Telegram...")
        from bot.telegram_bot import main as bot_main
        bot_main()

    elif mode == "all":
        import threading
        print(f"Iniciando dashboard en http://localhost:{APP_PORT}")
        print("Iniciando bot de Telegram...")

        dashboard_thread = threading.Thread(
            target=uvicorn.run,
            args=("backend.app.main:app",),
            kwargs={"host": "0.0.0.0", "port": APP_PORT},
            daemon=True,
        )
        dashboard_thread.start()

        from bot.telegram_bot import main as bot_main
        bot_main()

    else:
        print(f"Modo desconocido: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
