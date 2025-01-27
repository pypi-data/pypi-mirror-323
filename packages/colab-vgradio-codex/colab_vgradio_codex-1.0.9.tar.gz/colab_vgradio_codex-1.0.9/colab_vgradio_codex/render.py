from moviepy.editor import VideoFileClip, concatenate_videoclips

# Función para unir videos
def unir_videos():
    # Directorio donde están los videos
    input_folder = '/content/VIDU/video_output/'

    # Obtener todos los archivos .mp4 en el directorio
    try:
        videos_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    except FileNotFoundError:
        print(f"Error: El directorio '{input_folder}' no existe.")
        return None, "Error: No se encontró el directorio de videos."
    except Exception as e:
        print(f"Error al listar archivos de video: {str(e)}")
        return None, f"Error al listar archivos de video: {str(e)}"

    # Ordenar los archivos alfabéticamente para respetar la numeración
    videos_files.sort()

    # Crear lista para almacenar los clips de video
    clips = []
    listavideos = []  # Para almacenar los nombres de los videos

    # Cargar cada video y agregarlo a la lista de clips
    try:
        for video_file in videos_files:
            video_path = os.path.join(input_folder, video_file)
            clip = VideoFileClip(video_path)  # Cargar el video
            clips.append(clip)
            listavideos.append(video_file)  # Agregar el nombre del video a la lista
    except Exception as e:
        print(f"Error al cargar los videos: {str(e)}")
        return None, f"Error al cargar los videos: {str(e)}"


    # Imprimir la lista de los videos que se unieron
    print("Los videos que se unieron son:")
    for video_name in listavideos:
        print(video_name)

    # Concatenar todos los videos
    try:
        final_video = concatenate_videoclips(clips)
    except Exception as e:
        print(f"Error al concatenar videos: {str(e)}")
        return None, f"Error al concatenar videos: {str(e)}"


    # Guardar el archivo final en el sistema
    output_path = '/content/VIDU/video/video.mp4'
    try:
        final_video.write_videofile(output_path, codec='libx264')
    except Exception as e:
        print(f"Error al escribir el archivo de video: {str(e)}")
        return None, f"Error al escribir el archivo de video: {str(e)}"


    # Cerrar el video final para liberar recursos
    final_video.close()

    # Eliminar todo el contenido de la carpeta /content/VIDU/video_output
    try:
        for video_file in videos_files:
            video_path = os.path.join(input_folder, video_file)
            os.remove(video_path)  # Eliminar el archivo de video
    except Exception as e:
        print(f"Error al eliminar los archivos de video: {str(e)}")
        return output_path, f"Video unido con error al eliminar archivos: {str(e)}"


    # Retornar tanto el path del archivo generado como la lista de videos
    return output_path, '\n'.join(listavideos)  # Devuelve la lista como texto