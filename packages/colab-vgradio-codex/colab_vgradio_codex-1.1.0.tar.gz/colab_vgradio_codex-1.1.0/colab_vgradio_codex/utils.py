import re
import random
import string
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

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

def generar_nombre_completo():
    """Genera un nombre completo triplicando el nombre y apellido, junto con un número aleatorio de 3 dígitos."""
    nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
               "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
               "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
               "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa",
               # Nombres comunes de EE.UU.
               "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Charles", "Thomas",
               "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
               "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
               "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
               "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
               "Tyler", "Aaron", "Henry", "Douglas", "Jose", "Peter", "Adam", "Zachary", "Nathan", "Walter", 
               "Kyle", "Harold", "Carl", "Arthur", "Gerald", "Roger", "Keith", "Jeremy", "Terry", "Lawrence",
               "Sean", "Christian", "Ethan", "Austin", "Joe", "Jordan", "Albert", "Jesse", "Willie", "Billy"]

    apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
                 "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez",
                 "Gil", "Lopez", "Ramirez", "Santos", "Castro", "Suarez", "Munoz", "Gomez", "Gonzalez", "Navarro",
                 "Dominguez", "Lopez", "Rodriguez", "Sanchez", "Perez", "Garcia", "Gonzalez", "Martinez", "Fernandez", "Lopez",
                 # Apellidos comunes de EE.UU.
                 "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                 "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                 "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                 "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
                 "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
                 "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
                 "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
                 "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood"]


    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    numero = random.randint(100, 999)

    nombre_completo = f"{nombre}_{apellido}_{numero}"
    return nombre_completo

def generar_contrasena():
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + "0123456789" + "#$%&/()@_-*+[]"
    longitud = 10
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña

def enviar_formulario(url, datos):
    """Envía una solicitud POST a un formulario web."""
    response = requests.post(url, data=datos)
    return response

def extraer_dominios(response_text):
    """Extrae dominios de un texto utilizando expresiones regulares."""
    dominios = re.findall(r'id="([^"]+\.[^"]+)"', response_text)
    return dominios

def obtener_sitio_web_aleatorio(response_text):
    """Obtiene un sitio web aleatorio de los dominios extraídos."""
    dominios = extraer_dominios(response_text)
    sitio_web_aleatorio = random.choice(dominios)
    return sitio_web_aleatorio
