import time
from colab_vgradio_codex.utils import generar_contrasena, generar_nombre_completo, enviar_formulario, obtener_sitio_web_aleatorio
from colab_vgradio_codex.auth import send_auth_code, login_to_vidu
from colab_vgradio_codex.email_utils import get_verification_code, delete_temp_mail
import os
API_KEY = os.environ.get("API_KEY")

def register():
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

    print(f'Email: {nombre_completo}@{sitio_domain}')

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
        print(f"Código de verificación: {verification_code}")
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
