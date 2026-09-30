"""Configuración protegida y Telegram sin reintentos de efectos externos."""
import base64
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr


class ErrorTelegram(Exception):
    """Solo códigos y textos propios; nunca incluir respuestas o URLs externas."""
    def __init__(self, codigo: str, mensaje: str, *, incierto: bool = False):
        super().__init__(mensaje)
        self.codigo = codigo
        self.incierto = incierto


@dataclass(frozen=True)
class ResultadoEnvio:
    estado: str
    codigo: str | None = None
    detalle: str | None = None
    message_id: int | None = None
    fecha_telegram: datetime | None = None


def validar_token(token: str) -> str:
    token = token.strip()
    if not re.fullmatch(r"[1-9][0-9]{0,19}:[A-Za-z0-9_-]{20,200}", token):
        raise ErrorTelegram("TOKEN_INVALIDO", "Revisa el formato del token de BotFather.")
    return token


class ConfiguracionTelegram:
    """Fernet con clave derivada y separada por dominio del secreto de instalación.

    El volumen solo contiene ciphertext; JWT_SECRET no se almacena allí. Conservar
    ambos en respaldo local protegido. Cambiar JWT_SECRET exige guardar el token otra vez.
    """
    def __init__(self):
        self.ruta = Path(os.getenv("TELEGRAM_CONFIG_DIR", "telegram_secrets")) / "bot.enc"

    def _cifrador(self) -> Fernet:
        clave = os.getenv("JWT_SECRET", "")
        if len(clave) < 32:
            raise ErrorTelegram("SECRETO_INSTALACION_INVALIDO", "La instalación necesita un JWT_SECRET de al menos 32 caracteres.")
        derivada = hashlib.sha256(b"foodsave:telegram:v1\0" + clave.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(derivada))

    def leer(self) -> SecretStr:
        try:
            if self.ruta.exists():
                return SecretStr(self._cifrador().decrypt(self.ruta.read_bytes()).decode())
            return SecretStr(os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
        except (OSError, InvalidToken, UnicodeError):
            raise ErrorTelegram("CONFIGURACION_ILEGIBLE", "No se pudo leer la configuración protegida. Guarda nuevamente el token.") from None

    def guardar(self, token: SecretStr) -> None:
        contenido = self._cifrador().encrypt(token.get_secret_value().encode())
        temporal = None
        try:
            self.ruta.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            fd, temporal = tempfile.mkstemp(dir=self.ruta.parent, prefix=".bot-")
            with os.fdopen(fd, "wb") as archivo:
                archivo.write(contenido)
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(temporal, self.ruta)
        except OSError:
            raise ErrorTelegram("CONFIGURACION_NO_GUARDADA", "No se pudo guardar la configuración protegida.") from None
        finally:
            if temporal and os.path.exists(temporal):
                os.unlink(temporal)


class SinRedireccion(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ClienteTelegram:
    def __init__(self, token: SecretStr):
        self._token = token

    @classmethod
    def desde_configuracion(cls):
        return cls(ConfiguracionTelegram().leer())

    @property
    def huella(self) -> str | None:
        valor = self._token.get_secret_value()
        return hashlib.sha256(valor.encode()).hexdigest() if valor else None

    def _consultar(self, metodo: str, datos: dict | None = None) -> dict | list:
        token = self._token.get_secret_value()
        if not token:
            raise ErrorTelegram("TOKEN_NO_CONFIGURADO", "Guarda el token del bot para continuar.")
        token = validar_token(token)
        peticion = Request(f"https://api.telegram.org/bot{token}/{metodo}",
                           data=json.dumps(datos or {}).encode(),
                           headers={"Content-Type": "application/json"}, method="POST")
        try:
            # urllib no registra las URLs (incluyen el token). Sin redirects ni retry.
            with build_opener(SinRedireccion()).open(peticion, timeout=8) as respuesta:
                contenido = respuesta.read(1_000_001)
            if len(contenido) > 1_000_000:
                raise ValueError
            resultado = json.loads(contenido)
            tipo = list if metodo == "getUpdates" else dict
            if not isinstance(resultado, dict) or resultado.get("ok") is not True or not isinstance(resultado.get("result"), tipo):
                raise ValueError
            return resultado["result"]
        except HTTPError as error:
            codigo = error.code
            error.close()
            if codigo == 401:
                raise ErrorTelegram("TOKEN_RECHAZADO", "Telegram rechazó el token. Reemplázalo con el de BotFather.") from None
            if codigo in (400, 403, 404):
                raise ErrorTelegram("TELEGRAM_RECHAZADO", "Telegram rechazó la consulta. Revisa el bot, el chat y sus permisos.") from None
            if codigo == 429:
                raise ErrorTelegram("TELEGRAM_LIMITE", "Telegram solicita esperar. Vuelve a comprobar más tarde.") from None
            raise ErrorTelegram("TELEGRAM_NO_DISPONIBLE", "Telegram no está disponible. Revisa el resultado antes de un nuevo envío.", incierto=metodo == "sendMessage") from None
        except (URLError, TimeoutError, OSError):
            raise ErrorTelegram("TELEGRAM_SIN_CONEXION", "No se pudo confirmar el resultado de Telegram. Revisa la conexión y el chat.", incierto=metodo == "sendMessage") from None
        except (ValueError, UnicodeError):
            raise ErrorTelegram("TELEGRAM_RESPUESTA_INVALIDA", "Telegram devolvió una respuesta inválida.", incierto=metodo == "sendMessage") from None

    def enviar_mensaje(self, chat_id: str, texto: str) -> ResultadoEnvio:
        if not texto or len(texto.encode("utf-16-le")) // 2 > 4096:
            return ResultadoEnvio("FALLIDO", "MENSAJE_FUERA_DE_RANGO", "El pedido supera el tamaño permitido por Telegram.")
        try:
            resultado = self._consultar("sendMessage", {"chat_id": chat_id, "text": texto,
                "link_preview_options": {"is_disabled": True}})
            mensaje_id, fecha = resultado.get("message_id"), resultado.get("date")
            chat = resultado.get("chat")
            if type(mensaje_id) is not int or mensaje_id <= 0 or type(fecha) is not int or not isinstance(chat, dict) or str(chat.get("id")) != chat_id:
                raise ValueError
            return ResultadoEnvio("ENVIADO", message_id=mensaje_id,
                                  fecha_telegram=datetime.fromtimestamp(fecha, timezone.utc))
        except ErrorTelegram as error:
            return ResultadoEnvio("PENDIENTE_VERIFICACION" if error.incierto else "FALLIDO", error.codigo, str(error))
        except Exception:
            # No guardar excepciones de red o respuestas que pueden contener la URL/token.
            return ResultadoEnvio("PENDIENTE_VERIFICACION", "TELEGRAM_RESPUESTA_INVALIDA", "No se pudo acreditar el envío. Revisa el chat antes de intentar de nuevo.")

    def comprobar_bot(self) -> dict:
        bot = self._consultar("getMe")
        if bot.get("is_bot") is not True or type(bot.get("id")) is not int or bot["id"] <= 0:
            raise ErrorTelegram("TELEGRAM_RESPUESTA_INVALIDA", "No se pudo validar la identidad del bot.")
        return {"id": bot["id"], "nombre": str(bot.get("first_name", "Bot"))[:120],
                "username": str(bot.get("username", ""))[:64]}

    def verificar_chat(self, chat_id: str) -> bool:
        bot = self.comprobar_bot()
        chat = self._consultar("getChat", {"chat_id": chat_id})
        if str(chat.get("id")) != chat_id:
            raise ErrorTelegram("CHAT_NO_COINCIDE", "Telegram devolvió otro destino. Vincula el identificador numérico actual.")
        if chat.get("type") == "private":
            return True
        if chat.get("type") not in ("group", "supergroup"):
            raise ErrorTelegram("CHAT_NO_ADMITIDO", "Usa un chat privado o grupo propio de pruebas; no un canal.")
        miembro = self._consultar("getChatMember", {"chat_id": chat_id, "user_id": bot["id"]})
        estado = miembro.get("status")
        if estado in ("creator", "administrator"):
            return True
        if estado == "member" and chat.get("permissions", {}).get("can_send_messages") is True:
            return True
        if estado == "restricted" and miembro.get("is_member") is True and miembro.get("can_send_messages") is True:
            return True
        raise ErrorTelegram("CHAT_SIN_PERMISO", "El bot no tiene permiso para escribir en este grupo de pruebas.")

    def buscar_chats_pruebas(self) -> list[dict]:
        bot = self.comprobar_bot()
        webhook = self._consultar("getWebhookInfo")
        if webhook.get("url"):
            raise ErrorTelegram("BOT_CON_WEBHOOK", "Este bot tiene un webhook. Usa un bot exclusivo de FoodSave o vincula el chat_id manualmente.")
        # Sin offset: no confirma ni descarta actualizaciones. Sin allowed_updates:
        # no modifica la suscripción de otro consumidor del bot.
        actualizaciones = self._consultar("getUpdates", {"limit": 100, "timeout": 0})
        chats = {}
        for actualizacion in actualizaciones:
            if not isinstance(actualizacion, dict): continue
            mensaje = actualizacion.get("message", {})
            if not isinstance(mensaje, dict): continue
            texto = mensaje.get("text", "")
            if texto not in ("/start", "/start@" + bot["username"]): continue
            chat = mensaje.get("chat", {})
            if not isinstance(chat, dict) or chat.get("type") not in ("private", "group", "supergroup"): continue
            if type(chat.get("id")) is not int: continue
            identificador = str(chat["id"])
            chats[identificador] = {"chat_id": identificador, "tipo": chat["type"]}
        return list(chats.values())
