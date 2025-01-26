import os
from main import register
import requests
import uuid
import json


def finish_upload(jwt_token, id, etag):
    # URL de la solicitud PUT
    url = f"https://service.vidu.com/tools/v1/files/uploads/{id}/finish"

    # Encabezados para la solicitud PUT
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Accept-Language": "en",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cookie": f"sajssdk_2015_cross_new_user=1; Shunt=; JWT={jwt_token}; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22sHAHHREAEnsAISHs%22%2C%22gae28_aV%22%3A%22EGSRsHuEGyrVES-AuSgAIsGEnEgGu-snAEEuHE-EsGnAAA-EGSRsHuEGygEHHH%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24ki8r28_ergreere%22%3A%22z88O2%3A%2F%2Fiyymb682.fmmfkr.ymo%2F%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3EPq1HPsdlwFN8w93AWq0hwqlJQqTopZ38wqPMwFTaQF18wF3HQq0MwvAJpFNIwqdawFkqWq1EQFKaBv3liZ7ku67OV5kgu9G6iZHgiZNapa3cQF0EQFyJwX1swq0hQXKc36A%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%24aVr68a8c_kmfa6_aV%22%2C%22Cikbr%22%3A%22sHAHHREAEnsAISHs%22%7D%7D"
    }

    # Cuerpo de la solicitud PUT (en formato JSON)
    payload = {
        "id": id,
        "etag": etag
    }

    try:
        # Realizar la solicitud PUT
        response = requests.put(url, headers=headers, data=json.dumps(payload))

        # Verificar si la solicitud fue exitosa (status 200)
        response.raise_for_status()

        respuesta_json = response.json()

        if 'ssupload' in respuesta_json:
           print("Upload finish")

        # Procesar la respuesta en formato JSON
        return response.json()

    except requests.exceptions.RequestException as e:
        # Manejo de errores
        print(f"Error al enviar la solicitud: {e}")
        return None





def upload_image_to_s3(jwt_token, file_id, file_path, url, image_height, image_width):
    # Encabezados para la solicitud PUT
    headers = {
        "Connection": "keep-alive",
        "x-amz-meta-image-height": str(image_height),
        "x-amz-meta-image-width": str(image_width),
        "Content-Type": "image/png",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }

    try:
        # Abrir el archivo de imagen en modo binario
        with open(file_path, 'rb') as file:
            # Realizar la solicitud PUT con el contenido del archivo
            response = requests.put(url, headers=headers, data=file)
            print(response.status_code)
            # Verificar si la solicitud fue exitosa (status 200)
            response.raise_for_status()

            # Verificando el estado de la respuesta
            if response.status_code == 200:
                  # Capturando los encabezados de la respuesta
                response_headers = response.headers
                # Extrayendo el valor del encabezado ETag
                etag = response_headers.get('ETag', 'Encabezado ETag no encontrado')

                etags  = etag.replace('"', '')

                # Ejemplo de uso
                response = finish_upload(jwt_token, file_id, etags)
                # Mostrar respuesta
                if response:
                    print("Respuesta del servidor:")

                return etag.replace('"', '')
            else:
                raise Exception(f"Error al subir el archivo: {response.status_code}")


            # Si la respuesta es exitosa, procesar la respuesta (puede ser JSON)
            return response.json()

    except requests.exceptions.RequestException as e:
        # Manejo de errores
        print(f"Error al enviar la solicitud: {e}")
        return None




def upload_file(jwt_token, image_width, image_height, file_path='/content/72105_345.mp4_00-00.png'):
    url = "https://service.vidu.com/tools/v1/files/uploads"

    headers = {
        "Connection": "keep-alive",
        "X-Request-Id": str(uuid.uuid4()),
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "en",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.vidu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.vidu.com/",
        "Cookie": f"sajssdk_2015_cross_new_user=1; Shunt=; JWT={jwt_token}; sensorsdata2015jssdkcross=dfm-enc-%7B%22Va28a6y8_aV%22%3A%22sHAHHREAEnsAISHs%22%2C%22gae28_aV%22%3A%22EGSRsHuEGyrVES-AuSgAIsGEnEgGu-snAEEuHE-EsGnAAA-EGSRsHuEGygEHHH%22%2C%22OemO2%22%3A%7B%22%24ki8r28_8eiggay_2mbeyr_8cOr%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24ki8r28_2rieyz_lrcMmeV%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24ki8r28_ergreere%22%3A%22z88O2%3A%2F%2Fiyymb682.fmmfkr.ymo%2F%22%7D%2C%22aVr68a8ar2%22%3A%22rc3liZ7ku67OV5kgPsGCiskkDskl3qmawFlAQh3EPq1HPsdlwFN8w93AWq0hwqlJQqTopZ38wqPMwFTaQF18wF3HQq0MwvAJpFNIwqdawFkqWq1EQFKaBv3liZ7ku67OV5kgu9G6iZHgiZNapa3cQF0EQFyJwX1swq0hQXKc36A%3D%22%2C%22za28mec_kmfa6_aV%22%3A%7B%226ior%22%3A%22%24aVr68a8c_kmfa6_aV%22%2C%22Cikbr%22%3A%22sHAHHREAEnsAISHs%22%7D%7D",
        "Accept-Encoding": "gzip, deflate"
    }

    # Datos JSON con parámetros editables
    data = {
        "scene": "vidu",
        "metadata": {
            "image-width": image_width,
            "image-height": image_height
        }
    }

    try:
        # Enviar la solicitud POST
        response = requests.post(url, headers=headers, json=data)

        # Procesar la respuesta
        response_json = response.json()
        file_id = response_json.get("id")
        put_url = response_json.get("put_url")

        # Mostrar los valores extraídos
        #print(f"ID: {file_id}")
        #print(f"PUT URL: {put_url}")

        if file_id and put_url:
          print("upload...")

          # Llamada a la función
          etag = upload_image_to_s3(jwt_token, file_id, file_path, put_url, image_height, image_width)

          # Mostrar respuesta
          if etag:
              print("Respuesta del servidor:", etag)



        return file_id, put_url, etag

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Error decoding JSON: {e}")




def upload(image_width, image_height, file_path):

      API_KEY = os.environ.get("JWT_TOKEN")
      # Verificar si la variable es None o está vacía
      if API_KEY:
          print("API_KEY tiene un valor:", API_KEY)
          jwt_token=API_KEY
          file_id, put_url, etag = upload_file(jwt_token, image_width, image_height,file_path)
          return file_id
      else:
          print("API_KEY está vacía o no está configurada.")
          register()
          API_KEY = os.environ.get("JWT_TOKEN")
          if API_KEY:
              print("API_KEY tiene un valor:", API_KEY)
              jwt_token=API_KEY
              file_id, put_url, etag = upload_file(jwt_token, image_width, image_height,file_path)
              return file_id
          else:
              print("API_KEY está vacía o no está configurada.")
              return None