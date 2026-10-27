# Dog Monitor 🐕

Monitoreo remoto de perros con Tapo C211, YOLO, Ollama y React Native.

---

## PASO 1: Backend Python

### Instalar dependencias

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configurar .env

```bash
copy .env.example .env
```
Editá `.env` con la IP de tu cámara, tu email y contraseña de Tapo.

**Cómo encontrar la IP de la cámara:**
- Abrí la app Tapo en el celular → Cámara → Información del dispositivo → IP

### Instalar Ollama (IA local)

1. Descargá desde https://ollama.com/download (Windows)
2. Instalá y ejecutá:
```bash
ollama pull llava
```
Esto descarga el modelo multimodal (puede tardar, son ~4GB).

### Iniciar el backend

```bash
python run.py
```

El servidor corre en `http://localhost:8000`.
Probá: `http://localhost:8000/health`

---

## PASO 2: Cloudflare Tunnel (acceso remoto)

### Instalar cloudflared

Descargá desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

### Ejecutar túnel temporal (gratis, sin cuenta)

```bash
cloudflared tunnel --url http://localhost:8000
```

Esto te da una URL pública del tipo `https://xxxxx.trycloudflare.com`.
Copiala para el siguiente paso.

---

## PASO 3: App móvil React Native

### Instalar Node.js y Expo

```bash
npm install -g expo-cli
cd mobile
npm install
```

### Configurar la URL del backend

```bash
copy .env.example .env
```
Editá `.env` y pegá tu URL de Cloudflare Tunnel:
```
EXPO_PUBLIC_API_URL=https://xxxxx.trycloudflare.com
```

### Ejecutar la app

```bash
npx expo start
```

Escaneá el QR con la app **Expo Go** en tu celular.

---

## Estructura del proyecto

```
dog-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py           ← FastAPI app
│   │   ├── modules/
│   │   │   ├── camera.py     ← Conexión Tapo C211 (RTSP + MJPEG)
│   │   │   ├── detector.py   ← Detección YOLO
│   │   │   ├── ai_reporter.py← Generación texto con Ollama (llava)
│   │   │   └── reporter.py   ← Loop cada 30s
│   │   └── routes/
│   │       ├── stream.py     ← GET /video-stream
│   │       └── reports.py    ← GET /latest-report, GET /history
│   ├── requirements.txt
│   └── .env.example
└── mobile/
    ├── app/
    │   ├── _layout.tsx       ← Navegación con tabs
    │   └── (tabs)/
    │       ├── index.tsx     ← Pantalla cámara en vivo
    │       ├── report.tsx    ← Último reporte IA
    │       └── history.tsx   ← Historial del día
    ├── constants/api.ts
    └── .env.example
```

## API Endpoints

| Endpoint | Descripción |
|---|---|
| `GET /health` | Estado del servidor |
| `GET /video-stream` | Stream MJPEG en vivo |
| `GET /latest-report` | Último reporte JSON |
| `GET /history` | Todos los reportes del día |
