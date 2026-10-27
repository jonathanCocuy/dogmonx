import base64
import logging
import os
import cv2
import httpx
import numpy as np

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava:13b")


def _frame_to_base64(frame: np.ndarray) -> str:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf.tobytes()).decode()


async def generate_report(frame: np.ndarray, detection: dict) -> str:
    """
    Sends frame + detection data to Ollama (llava) and returns a Spanish description.
    Falls back to a template-based message if Ollama is unavailable.
    """
    dogs = detection.get("dogs_count", 0)
    motion = detection.get("motion_score", 0)

    other = detection.get("other_objects", [])
    people_count = other.count("person")
    context_parts = [f"{dogs} perro(s) detectado(s) por sensor"]
    if people_count:
        context_parts.append(f"{people_count} persona(s) detectada(s) por sensor")

    sensor_hint = ""
    if dogs > 0:
        sensor_hint = f"(El sensor de movimiento detectó {dogs} perro(s) — puede haber más que no detectó.)"
    if people_count:
        sensor_hint += f" (También detectó {people_count} persona(s).)"

    prompt = (
        "Sos un sistema de vigilancia doméstica. Analizá visualmente esta imagen y describí el estado de los perros.\n\n"
        "Perros de la casa:\n"
        "- Layla: pelaje DORADO o CREMA\n"
        "- Haru: pelaje NEGRO\n\n"
        "INSTRUCCIÓN PRINCIPAL: Mirá la imagen con atención. Tu descripción se basa en lo que VES, no en sensores.\n"
        f"{sensor_hint}\n\n"
        "Formato de respuesta (máximo 2 oraciones):\n"
        "- Por cada perro que VES: '[Nombre] [acción] [ubicación].' (ej: 'Layla duerme en el sofá.')\n"
        "- Por cada perro que NO VES en la imagen: '[Nombre] fuera de cámara.'\n"
        "- Si no hay ningún perro visible: 'Layla y Haru fuera de cámara.'\n\n"
        "Reglas:\n"
        "1. Identificá por color: dorado/crema = Layla, negro = Haru.\n"
        "2. Ubicación: usá objetos ('en el sofá', 'en el piso', 'junto a la puerta'). NUNCA nombres de habitaciones.\n"
        "3. Cero introducciones. Cero descripciones de muebles o ambiente.\n\n"
        "Responde directo. Ejemplo: 'Layla duerme en el sofá al centro. Haru fuera de cámara.'"
    )

    try:
        img_b64 = _frame_to_base64(frame)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "images": [img_b64],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json()["response"].strip()
    except Exception as exc:
        logger.warning("Ollama unavailable (%s), using fallback report", exc)
        return _fallback_report(dogs, motion)


def _fallback_report(dogs: int, motion: float) -> str:
    if dogs == 0:
        return "No se detectaron perros en el encuadre."
    if motion < 0.05:
        return f"{'Un perro está' if dogs == 1 else 'Los perros están'} descansando tranquilamente."
    if motion < 0.2:
        return f"{'Un perro se mueve' if dogs == 1 else 'Los perros se mueven'} levemente."
    return f"{'Un perro está' if dogs == 1 else 'Los perros están'} muy activos."
