import cv2
import os
import shutil
import subprocess

def extraer_ultimo_fotograma(video_path, output_image_path):
    """
    Extrae el último fotograma de un video y lo guarda como una imagen JPG con calidad 100%.
    Luego copia el video a la carpeta '/content/video_output' con numeración secuencial.
    
    :param video_path: Ruta del archivo de video (ej. '/content/video.mp4')
    :param output_image_path: Ruta donde se guardará el fotograma como imagen (ej. '/content/img_fragmento.jpg')
    """
    # Método 1: Usando OpenCV (si está disponible)
    try:
        # Capturamos el video
        video = cv2.VideoCapture(video_path)

        # Obtenemos el número total de fotogramas
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Nos desplazamos al último fotograma
        video.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)

        # Leemos el último fotograma
        ret, frame = video.read()

        # Si el fotograma fue leído correctamente, lo guardamos como imagen con calidad 100%
        if ret:
            # Guardamos la imagen con calidad 100%
            cv2.imwrite(output_image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            print(f'Último fotograma guardado con calidad 100% (OpenCV)')
        else:
            print('Error al leer el último fotograma (OpenCV)')

        # Liberamos el objeto video
        video.release()

    except Exception as e:
        print(f"Error al usar OpenCV: {e}")

        # Método 2: Usando FFmpeg (si OpenCV falla)
        # Obtiene la duración del video
        duracion_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        duracion = float(subprocess.check_output(duracion_cmd))

        # Calcula el tiempo para buscar cerca del final (0.1 segundos antes)
        tiempo_busqueda = str(duracion - 0.1)

        # Construye el comando FFmpeg para extraer el último fotograma
        comando = [
            "ffmpeg",
            "-ss", tiempo_busqueda,  # Busca cerca del final
            "-i", video_path,
            "-vframes", "1",  # Extrae solo un fotograma
            "-qscale:v", "2",  # Ajusta la calidad si es necesario
            output_image_path
        ]

        # Ejecuta el comando FFmpeg
        subprocess.run(comando)
        print(f'Último fotograma guardado con calidad 100% (FFmpeg)')

    # Crear la carpeta '/content/video_output' si no existe
    output_folder = '/content/VIDU/video_output'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f'Carpeta creada...')
    
    # Verificar la numeración de los archivos en la carpeta
    existing_videos = sorted([f for f in os.listdir(output_folder) if f.endswith('.mp4')])
    
    if existing_videos:
        # Obtener el último número de archivo y aumentar en 1
        last_video = existing_videos[-1]
        last_number = int(last_video.split('.')[0])  # Extraer número del formato '00001.mp4'
        new_number = last_number + 1
    else:
        # Si no existen archivos, comenzar con '00001'
        new_number = 1

    # Formatear el nuevo nombre del archivo con ceros iniciales
    new_video_name = f'{new_number:05}.mp4'
    new_video_path = os.path.join(output_folder, new_video_name)

    # Copiar el video original a la nueva ruta con numeración
    shutil.copy(video_path, new_video_path)
    print(f'Video copiado como...')


