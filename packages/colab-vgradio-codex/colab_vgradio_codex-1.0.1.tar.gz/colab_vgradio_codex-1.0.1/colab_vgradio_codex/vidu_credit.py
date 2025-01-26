import json
import os
import requests
from colab_vgradio_codex.main import register
import time

def creditos_api(credit):
    API_KEY = os.environ.get("JWT_TOKEN")
    # Verificar si la variable es None o está vacía
    if API_KEY:
        print("API KEY Valid")
        vall = get_credits(credit)
    else:
        print("API KEY está vacía o no está configurada.")
        register()
        API_KEY = os.environ.get("JWT_TOKEN")
        if API_KEY:
            print("API KEY Valid")
            vall = get_credits(credit)
            return vall
        else:
            return None
    return vall
def get_credits(credit):
    
    jwt_token = os.environ.get("JWT_TOKEN")
    url = "https://service.vidu.com/credit/v1/credits/me"
    headers = {
        "Host": "service.vidu.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": f"sajssdk_2015_cross_new_user=1; Shunt=; JWT={jwt_token}; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22sHAHHREAEnsAISHs%22%2C%22gae28_aV%22%3A%22EGSRsHuEGyrVES-AuSgAIsGEnEgGu-snAEEuHE-EsGnAAA-EGSRsHuEGygEHHH%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24ki8r28_ergreere%22%3A%22z88O2%3A%2F%2Fiyymb682.fmmfkr.ymo%2F%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3EPq1HPsdlwFN8w93AWq0hwqlJQqTopZ38wqPMwFTaQF18wF3HQq0MwvAJpFNIwqdawFkqWq1EQFKaBv3liZ7ku67OV5kgu9G6iZHgiZNapa3cQF0EQFyJwX1swq0hQXKc36A%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%24aVr68a8c_kmfa6_aV%22%2C%22Cikbr%22%3A%22sHAHHREAEnsAISHs%22%7D%7D"
    }

    try:
        # Realizar el request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza un error si el código de estado no es 2xx

        # Convertir el JSON de respuesta
        data = response.json()
        # Extraer el valor de 'credits'
        available_credits = data.get('credits', 0)
        print("Credit:", available_credits)

        if not (credit <= available_credits):
            register()
            time.sleep(1)
            valor = get_credits(credit)
            return valor

        # Comparar y devolver el resultado
        return credit <= available_credits

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return False
    except ValueError:
        print("Error al decodificar el JSON.")
        return False
