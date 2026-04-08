# Google Workspace Automation

Automatiza tus tareas diarias de Google Workspace con inteligencia artificial. Dashboard web + Bot de Telegram para gestionar Gmail, Calendar, Drive y Sheets desde cualquier lugar.

## Funcionalidades

### Gmail
- Ver emails no leidos y hacer triage por prioridad
- Responder emails con IA (lenguaje natural)
- Enviar emails nuevos
- Resumen inteligente del inbox

### Google Calendar
- Ver agenda del dia y de la semana
- Crear y cancelar eventos
- Notificaciones de proximas reuniones

### Google Drive
- Listar archivos recientes
- Buscar archivos por nombre o contenido
- Ver informacion de almacenamiento

### Google Sheets
- Leer y escribir datos
- Generar reportes automaticos
- Agregar filas de datos

### Bot de Telegram
- `/inbox` - Ver emails no leidos
- `/triage` - Clasificar emails por prioridad
- `/resumen` - Resumen inteligente con IA
- `/agenda` - Eventos de hoy
- `/semana` - Eventos de la semana
- `/archivos` - Archivos recientes en Drive
- `/buscar [texto]` - Buscar en Drive
- `/responder` - Responder email con IA

## Arquitectura

```
google-workspace-automation/
├── automations/          # Logica de automatizacion
│   ├── gmail_automation.py
│   ├── calendar_automation.py
│   ├── drive_automation.py
│   ├── sheets_automation.py
│   └── ai_assistant.py
├── backend/              # API REST (FastAPI)
│   └── app/
│       ├── main.py
│       └── routers/
├── bot/                  # Bot de Telegram
│   └── telegram_bot.py
├── dashboard/            # Frontend web
│   ├── templates/
│   └── static/
├── config/               # Configuracion y auth
│   ├── settings.py
│   └── google_auth.py
└── run.py                # Punto de entrada
```

## Stack Tecnologico

- **Backend**: Python + FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Bot**: python-telegram-bot
- **AI**: Claude API (Anthropic)
- **APIs**: Google APIs (Gmail, Calendar, Drive, Sheets)
- **Auth**: OAuth 2.0

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/mbdata-sharon/google-workspace-automation.git
cd google-workspace-automation
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo
3. Habilita las APIs: Gmail, Calendar, Drive, Sheets
4. Crea credenciales OAuth 2.0 (tipo "Aplicacion de escritorio")
5. Descarga el archivo `credentials.json` y ponlo en la raiz del proyecto

### 5. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### 6. Crear bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un bot nuevo con `/newbot`
3. Copia el token y ponlo en `.env`

### 7. Ejecutar

```bash
# Solo dashboard
python run.py dashboard

# Solo bot de Telegram
python run.py bot

# Ambos
python run.py all
```

## Demo

### Dashboard Web
El dashboard muestra un resumen de tu Google Workspace: emails, calendario, archivos y almacenamiento. Puedes responder emails con IA directamente desde la interfaz.

### Bot de Telegram
Desde tu celular, controla todo tu workspace con comandos simples. El bot genera respuestas con IA y siempre pide tu confirmacion antes de enviar.

## Tecnologias Usadas

| Tecnologia | Uso |
|---|---|
| Python 3.11+ | Lenguaje principal |
| FastAPI | Backend REST API |
| Google APIs | Gmail, Calendar, Drive, Sheets |
| python-telegram-bot | Bot de Telegram |
| Claude API | Generacion de respuestas con IA |
| HTML/CSS/JS | Dashboard web |
| OAuth 2.0 | Autenticacion segura |

## Autora

**Sharon Leon** - [GitHub](https://github.com/mbdata-sharon)

Marketing B2B & Data Science | Automatizacion con IA
