from main import register
import requests
import json
import time
import os
import uuid

def eliminar_tarea(task_id, jwt_token):
    url = f"https://service.vidu.com/vidu/v1/tasks/{task_id}"
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
        "Cookie": f"JWT={jwt_token}; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22sSGtAEnGtEnnGsEA%22%2C%22gae28_aV%22%3A%22EGSRsHuEGyrVES-AuSgAIsGEnEgGu-snAEEuHE-EsGnAAA-EGSRsHuEGygEHHH%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24ki8r28_ergreere%22%3A%22z88O2%3A%2F%2Fiyymb682.fmmfkr.ymo%2F%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3EPq1HPsdlwFN8w93AWq0hwqlJQqTopZ38wqPMwFTaQF18wF3HQq0MwvAJpFNIwqdawFkqWq1EQFKaBv3liZ7ku67OV5kgu9G6iZHgiZNapa3cQXlSwX1spFfJQqPHwq1M36A%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%24aVr68a8c_kmfa6_aV%22%2C%22Cikbr%22%3A%22sSGtAEnGtEnnGsEA%22%7D%7D",
        "Accept-Encoding": "gzip, deflate"
    }

    response = requests.delete(url, headers=headers)

    # Validación de la respuesta
    if response.status_code == 200:
        print("\nCuerpo de la respuesta:")
        print(response.text if response.text else "{} (JSON vacío)")
    else:
        print(f"Error: Código de estado {response.status_code}")
        print("Detalles de la respuesta:")
        print(response.text)


def download_video(url, save_path, video_name, jwt_token, task_id):
    try:
        # Crear la carpeta si no existe
        os.makedirs(save_path, exist_ok=True)

        # Ruta completa del archivo
        file_path = os.path.join(save_path, video_name)

        # Si el archivo ya existe, se eliminará
        if os.path.exists(file_path):
            print(f"El archivo ya existe. Será reemplazado: {file_path}")
            os.remove(file_path)

        # Descargar el archivo
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Verifica si hay errores en la respuesta

        # Guardar el contenido en un archivo
        with open(file_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=8192):  # Descargar en partes
                if chunk:
                    video_file.write(chunk)

        print(f"Video descargado exitosamente en: {file_path}")
        # Llama a la función con los parámetros necesarios
        #eliminar_tarea(task_id, jwt_token)

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el video: {e}")
    except OSError as e:
        print(f"Error al crear la carpeta o guardar el archivo: {e}")


def get_credits_from_api(jwt_token, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type, creditos):

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
        credits = data.get('credits', 0)

        if creditos <= credits:
            task_id, response_contents, video_url, additional_id = enviar_tarea(jwt_token, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type)
            os.environ["TASK_ID"] = task_id
            os.environ["VIDEO_URL"] = video_url
            os.environ["ADDITIONAL_ID"] = additional_id
            #print(f"Status Code: {task_id}")
            #print(f"Response Body: {response_contents}")
            #print(f"Video URL: {video_url}")
            #print(f"Additional ID: {additional_id}")
            print("Generate Image to Video...")
            print("Credits:", credits)
        else:
            print("No se encontraron créditos suficientes.")
            register()
            time.sleep(1)
            API_KEY = os.environ.get("JWT_TOKEN")
            jwt_token1=API_KEY
            # Llamar a la función y mostrar el resultado
            task_id, response_contents, video_url, additional_id = enviar_tarea(jwt_token1, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type)
            os.environ["TASK_ID"] = task_id
            os.environ["VIDEO_URL"] = video_url
            os.environ["ADDITIONAL_ID"] = additional_id
            print("Generate Image to Video...")
            print("Credits:", credits)

        return data.get('credits', 0)

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return 0
    except ValueError:
        print("Error al decodificar el JSON.")
        return 0


def procesoo_tarea(jwt_token, task_id):

    url = f"https://service.vidu.com/vidu/v1/tasks/{task_id}"
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": f"JWT={jwt_token}"
    }

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Verificar si la tarea está en estado "success"
            if data.get("state") == "success":
                # Intentar obtener la URL del video y el ID adicional
                creations = data.get("creations", [])
                for creation in creations:
                    if creation.get("type") == "video" and "uri" in creation:
                        video_url = creation["uri"]
                        creation_id = creation.get("id")

                        if creation_id:
                          os.environ["CREATION_ID"] = creation_id

                        # Parámetros
                        save_directory = "/content/VIDU/video"
                        video_filename = "video.mp4"
                        # Llamar a la función para descargar el video
                        download_video(video_url, save_directory, video_filename, jwt_token, task_id)

                        return video_url, creation_id

                print("Estado 'success' encontrado, pero no se encontraron datos.")
            else:
                print(f"Estado actual: {data.get('state')}. Esperando...")
        else:
            print(f"Error en la solicitud. Código: {response.status_code}. Detalle: {response.text}")

        # Esperar 10 segundos antes del próximo intento
        time.sleep(10)

def enviar_tarea(jwt_token, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type):
    url = "https://service.vidu.com/vidu/v1/tasks"

    headers = {
        "Host": "service.vidu.com",
        "Connection": "keep-alive",
        "X-Request-Id": str(uuid.uuid4()),
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "x-recaptcha-token": "Task_Submit",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "X-Aws-Waf-Token": "d7457453-4a52-47bc-8da0-1980cc057759:EAoApQCBsY6CAAAA:n2zFX1/YkxDe/9ERFq4O8P4GDhDy9RlrXV+MDSZ4IsLrJoRDSsWGpLXiEBwQWPfturRHFRs4CQVQKinKfB2S5gN4NM+JDCtX7I2riM6jFJLlqQQVv0d1rj0i+C9ke8NSXuOG7V8dereCF2mkzJHhMBfzlqc65hXKdLCS7z/NbUC6rp3+iknvf0SxveuLU6Q5iEapizHped1Awfjn71ltHUxyFnGIETMZYtoEaeH9AvOoH7S+Ng==",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": f"sajssdk_2015_cross_new_user=1; JWT={jwt_token}; Shunt=; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22snEstssAIHGtHEHH%22%2C%22gae28_aV%22%3A%22EGSRgyiuttAHtE-AnIEGHiiuyiHRtS-snAEEuHE-EsGnAAA-EGSRgyiuttEHVE%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24ki8r28_ergreere%22%3A%22%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQsWqPZ3SpX0EpX18wXPhwFlEPZTaPs1EQhfABF3swX1JPqKJBF1cpFPMwX08wFlAQsWqPZ3SpX1EWX1aBv3liZ7ku67OV5kgu9G6iZHgiZNapa3cQq1cpX3cwXwEpFfEwFKE36A%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%24aVr68a8c_kmfa6_aV%22%2C%22Cikbr%22%3A%22snEstssAIHGtHEHH%22%7D%7D",
        "Accept-Encoding": "gzip, deflate",
    }

    data = {
        "input": {
            "prompts": [
                {"type": "text", "content": content_text},
                {"type": "image", "content": f"ssupload:?id={content_image_id}", "src_imgs": [f"ssupload:?id={content_image_id}"]}
            ],
            "enhance": enhance
        },
        "type": task_type,
        "settings": {
            "style": style,
            "duration": duration,
            "model": model,
            "schedule_mode": schedule_mode,
            "model_version": model_version
        }
    }

    # Realizar la solicitud POST
    try:
        response = requests.post(url, headers=headers, json=data)
        #print("Response Status Code:", response.status_code)  # Verifica el código de estado
        #print("Response Text:", response.text)  # Verifica el contenido de la respuesta

        response_data = response.json()  # Esto puede fallar si no es JSON

        if 'message' in response_data and 'insufficient credits' in response_data['message']:
            print("sin créditos")
            register()
            time.sleep(1)
            API_KEY = os.environ.get("JWT_TOKEN")
            jwt_token1=API_KEY
            task_id, response_contents, video_url, additional_id = enviar_tarea(jwt_token1, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type)
            os.environ["TASK_ID"] = task_id
            os.environ["VIDEO_URL"] = video_url
            os.environ["ADDITIONAL_ID"] = additional_id

            return None, None, None, None
        else:
            # Proceder con el resto de la lógica
            task_id = response_data.get('id', None)
            response_prompts = response_data.get('input', {}).get('prompts', [])
            response_contents = ", ".join(prompt.get('content', '') for prompt in response_prompts)

            if task_id:
                result = procesoo_tarea(jwt_token, task_id)

                if result:
                    video_url, additional_id = result
                    return task_id, response_contents, video_url, additional_id
                else:
                    print("No se encontraron resultados.")
                    return None, None, None, None
            else:
                print("No se pudo obtener el ID de la tarea.")
                return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")
        return None, None, None, None
    except ValueError as e:
        print(f"Error al analizar la respuesta JSON: {e}")
        return None, None, None, None


# Ejemplo de llamada a la función



def img_to_video_10(content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type, creditos):

    API_KEY = os.environ.get("JWT_TOKEN")
    # Verificar si la variable es None o está vacía
    if API_KEY:
        print("API KEY Valid")
        API_KEY = os.environ.get("JWT_TOKEN")
        print(API_KEY)
        jwt_token=API_KEY
        # Llamar a la función y mostrar el resultado
        credits = get_credits_from_api(jwt_token, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type, creditos)

        print("Credits:", credits)
        
    else:
        print("API KEY está vacía o no está configurada.")
        register()
        API_KEY = os.environ.get("JWT_TOKEN")
        if API_KEY:
            print("API KEY Valid")
            API_KEY = os.environ.get("JWT_TOKEN")
            jwt_token=API_KEY
            # Llamar a la función y mostrar el resultado
            credits = get_credits_from_api(jwt_token, content_text, content_image_id, enhance, style, duration, model, schedule_mode, model_version, task_type, creditos)

            print("Credits:", credits)
        else:
            print("API KEY está vacía o no está configurada.")