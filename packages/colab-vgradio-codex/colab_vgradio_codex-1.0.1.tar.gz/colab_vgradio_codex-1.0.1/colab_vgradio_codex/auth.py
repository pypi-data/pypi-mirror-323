import requests
import uuid


def extract_jwt_cookie(cookies):
    """Extrae el valor de la cookie JWT."""
    jwt_token = cookies.get('JWT')
    return jwt_token

def leer_token():
    try:
        with open("/tmp/token_swt.txt", "r") as file:
            token = file.read()  # Leer el contenido del archivo
            if token:
                return token  # Devuelve el token si se encontró
            else:
                return "El archivo está vacío o no contiene un token."
    except Exception as e:
        return f"Error al leer el archivo: {e}"


def login_to_vidu(identity, credential, token_aws):

    url = "https://service.vidu.com/iam/v1/users/login"
    headers = {
        "Connection": "keep-alive",
        "X-Request-Id": str(uuid.uuid4()),
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "x-recaptcha-token": "Login",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "X-Aws-Waf-Token": "f5246f38-7ab5-4510-96eb-d77bc7d8ae70:EAoAlMIhKSQUAAAA:Jj0nrjYRLfsNEugUzXRwOfAza7B5Lo75bzWkueT5YfSQ+ZhLHSDMrs/WV7XLj2xG8HqU56S1G1J6caauuNd5WRwaTXtZfLHEYdNIG0yf59sV/KLTfELfF+4gvr9JchdTdKWhW3hullY/2jB0TT8Qef0vJVfrFXAAV5LU4WvGLccz4MPCT+34iuqktf4aO1Dh9/AQfIHeCIAVoD7sQXCjD1n1n3NUk6P2GNMsNxTNz7U4KR3BZA==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": "sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22EGSRsGtyguEIsS-AtuHtVtHERtRII-snAEEuHE-EsGnAAA-EGSRsGtygusEAEV%22%2C%22gae28_aV%22%3A%22%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24ki8r28_ergreere%22%3A%22%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3Hp9QoPq1hwqN8wXzaQFzlpXKJQhfIwhw8wqPMwFTaQF18wF3HQq0MwvAJpFNIwqlSPsWawq1MwZNagN%3D%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%22%2C%22Cikbr%22%3A%22%22%7D%7D",
        "Accept-Encoding": "gzip, deflate"
    }
    data = {
        "id_type": "email",
        "identity": identity,
        "auth_type": "authcode",
        "credential": credential,
        "device_id": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción para errores HTTP
        respon = response.json()
        if respon:
            # Extraer el token de la respuesta
            token = respon.get('token', None)
            if token:
                print("Token extraído:", token)
            else:
                print("Token no encontrado en la respuesta.")

        return response.json(), token
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")
        return None, None

def send_auth_code(receiver, token_aws):
    url = "https://service.vidu.com/iam/v1/users/send-auth-code"
    headers = {
        "Connection": "keep-alive",
        "X-Request-Id": str(uuid.uuid4()),
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "x-recaptcha-token": "Auth_Code",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "X-Aws-Waf-Token": "f5246f38-7ab5-4510-96eb-d77bc7d8ae70:EAoAlMIhKSQUAAAA:Jj0nrjYRLfsNEugUzXRwOfAza7B5Lo75bzWkueT5YfSQ+ZhLHSDMrs/WV7XLj2xG8HqU56S1G1J6caauuNd5WRwaTXtZfLHEYdNIG0yf59sV/KLTfELfF+4gvr9JchdTdKWhW3hullY/2jB0TT8Qef0vJVfrFXAAV5LU4WvGLccz4MPCT+34iuqktf4aO1Dh9/AQfIHeCIAVoD7sQXCjD1n1n3NUk6P2GNMsNxTNz7U4KR3BZA==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": "sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22EGSRsGtyguEIsS-AtuHtVtHERtRII-snAEEuHE-EsGnAAA-EGSRsGtygusEAEV%22%2C%22gae28_aV%22%3A%22%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24ki8r28_ergreere%22%3A%22%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3Hp9QoPq1hwqN8wXzaQFzlpXKJQhfIwhw8wqPMwFTaQF18wF3HQq0MwvAJpFNIwqlSPsWawq1MwZNagN%3D%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%22%2C%22Cikbr%22%3A%22%22%7D%7D",
        "Accept-Encoding": "gzip, deflate"
    }
    data = {
        "channel": "email",
        "receiver": receiver,
        "purpose": "login",
        "locale": "en"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción para errores HTTP
        respuesta_json = response.json()
        
        # Comprobamos si 'sequence' está en la respuesta
        if 'sequence' in respuesta_json:
            res_json = "successful"
        else:
            res_json = f"Request failed with status code {response.status_code}"
        
        return res_json
        
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")
        return None
