import time
from colab_vgradio_codex.utils import generar_contrasena, generar_nombre_completo, enviar_formulario, obtener_sitio_web_aleatorio
from colab_vgradio_codex.auth import send_auth_code, login_to_vidu
from colab_vgradio_codex.email_utils import get_verification_code, delete_temp_mail
import requests
import re
import random
import string
import uuid
import time
import os

API_KEY = os.environ.get("API_KEY")

def create_email(min_name_length=10, max_name_length=10):
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    headers = {
        "Host": "api.internal.temp-mail.io",
        "Connection": "keep-alive",
        "Application-Name": "web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Application-Version": "3.0.0",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://temp-mail.io",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://temp-mail.io/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    data = {
        "min_name_length": min_name_length,
        "max_name_length": max_name_length
    }

    # Hacer la solicitud
    response = requests.post(url, json=data, headers=headers)

    # Extraer el email de la respuesta JSON
    if response.status_code == 200:
        email = response.json().get("email")
        return email
    else:
        return None


def get_verification_code(email):
    url = f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages"
    headers = {
        "Host": "api.internal.temp-mail.io",
        "Connection": "keep-alive",
        "Application-Name": "web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Application-Version": "3.0.0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://temp-mail.io",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://temp-mail.io/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }

    # Hacer la solicitud GET
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        if messages:
            # Extraer el código de verificación del cuerpo del texto
            body_text = messages[0].get("body_text", "")
            code = extract_code_from_text(body_text)
            return code
    return None

def extract_code_from_text(body_text):
    # Buscar un patrón de 6 dígitos en el texto
    match = re.search(r'\b\d{6}\b', body_text)
    if match:
        return match.group(0)
    return None

def check_code_with_retries(email, retries=6, delay=10):
    for attempt in range(retries):
        print(f"Intento {attempt + 1} de {retries}...")
        code = get_verification_code(email)
        if code:
            print(f"Código de verificación: ******")
            return code
        #print("Código no encontrado. Esperando 10 segundos antes de reintentar...")
        time.sleep(delay)
    print("Se alcanzó el máximo de intentos sin éxito.")
    return None


# Ejemplo de uso
def register():
    email = create_email()
    print(f'Email: *********@*****.com')
    time.sleep(1)
    token_swt = ""
    send_auth_code(email, token_swt)
    print("60 seconds")
    verification_code = check_code_with_retries(email)
    time.sleep(1)
    token_swt = "qwertt"
        # Realizar el login y obtener el JWT Token
    response, jwt_token = login_to_vidu(email, verification_code, token_swt)
    if jwt_token:
      print("Login exitoso. Token obtenido.")
      os.environ["JWT_TOKEN"] = jwt_token

def register2():
    # Ejemplo de uso
    url = 'https://email-fake.com/'

    # Supongamos que el formulario en el sitio web tiene un campo llamado 'campo_correo'
    datos = {'campo_correo': 'ejemplo@dominio.com'}

    # Enviar la solicitud POST al formulario
    response = enviar_formulario(url, datos)

    # Obtener un sitio web aleatorio de los dominios extraídos
    sitio_domain = obtener_sitio_web_aleatorio(response.text)

    # Generar y mostrar un nombre completo
    nombre_completo = generar_nombre_completo()

    #print(f'Email: {nombre_completo}@{sitio_domain}')
    print('Email: ***********@*******.com')

    time.sleep(3)

    email_reg = f"{nombre_completo}@{sitio_domain}"
    # Enviar código de autenticación al correo
    token_swt = ""

    send_auth_code(email_reg, token_swt)
    print("60 seconds")
    time.sleep(1)

    # Intentar obtener el código de verificación durante 60 segundos (6 intentos con una pausa de 10 segundos)
    verification_code = None
    identifier = None
    attempts = 20  # 6 intentos para un minuto (cada 10 segundos)
    for attempt in range(attempts):
        print(f"Attempt {attempt + 1} from {attempts}...")
        
        # Obtener el código de verificación y el identificador
        verification_code, identifier = get_verification_code(nombre_completo, sitio_domain)

        if verification_code and identifier:
            print(f"Código de verificación encontrado: {verification_code}")
            break  # Salir del bucle si se encuentra el código

        time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente

    if verification_code and identifier:
        #print(f"Código de verificación: {verification_code}")
        print(f"Código de verificación: *****")
        print(f"Identificador: {identifier}")
        time.sleep(3)
        print("Login...")
        token_swt = "qwertt"

        # Realizar el login y obtener el JWT Token
        response, jwt_token = login_to_vidu(email_reg, verification_code, token_swt)

        if jwt_token:
            print("Login exitoso. Token obtenido.")
            os.environ["JWT_TOKEN"] = jwt_token
    else:
        print("No se pudieron encontrar los datos necesarios.")

    time.sleep(3)

    # Eliminar el correo temporal
    delete_temp_mail(nombre_completo, sitio_domain, identifier)
