import random
import json
import requests
from tqdm.notebook import tqdm
import time
import hashlib
import base64
import os
from registro import *
from moviepy.video.io.VideoFileClip import VideoFileClip

def recortar_video(ruta_video):
    """
    Recorta un video eliminando una duración fija del inicio y del final,
    guardándolo con el mismo nombre y en la misma ruta, reemplazando el archivo original.
    
    Args:
        ruta_video (str): Ruta completa del archivo de video (entrada y salida).
    """
    # Duraciones fijas para recortar
    inicio_recorte = 0.13  # Recortar 0.13 segundos del inicio
    final_recorte = 0.15  # Recortar 0.15 segundos del final

    # Carga el video original
    clip = VideoFileClip(ruta_video)
    
    # Asegúrate de que los recortes no excedan la duración total
    duracion_total = clip.duration
    if inicio_recorte + final_recorte >= duracion_total:
        raise ValueError("La duración de recorte excede la duración total del video.")

    # Recorta el video
    nuevo_clip = clip.subclip(inicio_recorte, duracion_total - final_recorte)
    
    # Genera un archivo temporal en la misma ruta
    temp_output_path = "temp_" + os.path.basename(ruta_video)
    nuevo_clip.write_videofile(
        temp_output_path,
        codec="libx264",       # Usa un códec eficiente y ampliamente compatible
        audio_codec="aac",     # Mantiene el audio en un formato estándar
        preset="slow",         # Mejora la calidad de la compresión
        bitrate="3000k",       # Ajusta el bitrate para una calidad similar al original
        threads=4              # Usa múltiples hilos para mejorar el rendimiento
    )
    
    # Reemplaza el archivo original con el archivo temporal
    os.replace(temp_output_path, ruta_video)
    
    print(f"Video procesado y guardado en {ruta_video}")



def obteneravatar(access_token):
    url = "https://www.hedra.com/api/app/v1/app/projects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/app/characters",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    response = requests.get(url, headers=headers)
    return response.json()

def eliminar_proyecto(joob_id, access_token):
    url = f"https://www.hedra.com/api/app/v1/app/projects/{joob_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/app/characters",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    response = requests.delete(url, headers=headers)

    # Imprime el código de estado de la respuesta y el contenido de la respuesta
    #print(f"Status Code: {response.status_code}")
    #print(f"Response: {response.text}")



def video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode('utf-8')
    return video_base64


# Función para actualizar la barra de progreso y descargar el video si el progreso es 100%
def update_progress_bar(current_progress, ruta_video, access_token, joob_ids):
    total_steps = 100
    video_url = None
    while current_progress < 1.0:
        # Simula obtener el progreso actualizado
        response = obteneravatar(access_token)
        #print("Proceso:", response)
        project = response['projects'][0]
        current_progress = project['progress']
        video_url = project['videoUrl']  # Obtener la URL del video
        #print("Video URL:", video_url)
        
        # Calcular el contador de progreso
        step = int(current_progress * total_steps)

        os.environ["PROGRESS_HEDRA"] = str(step)
        
        # Imprimir el progreso en la misma línea
        print(f"\rProgreso: {step}%", end='', flush=True)
        
        time.sleep(2)  # Ajusta el intervalo de actualización aquí

    if video_url:  # Si se ha obtenido una URL del video, descarga el video
        download_video(video_url, ruta_video, access_token, joob_ids)



# Función para generar un nombre de archivo seguro a partir de una URL
def generate_safe_filename(url):
    # Usa un hash MD5 de la URL para generar un nombre de archivo único y seguro
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest() + '.mp4'

# Función para descargar el video desde una URL
def download_video(url, ruta_video, access_token, joob_ids):
    #print("url",url)
    os.makedirs('/tmp/videos_tts', exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename = generate_safe_filename(url)
        #print(url)
        #filename = "3424asdf.mp4"
        with open(f"{ruta_video}{filename}" , 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f" Video downloaded as {filename}")


        # Ejecutar la función
        eliminar_proyecto(joob_ids, access_token)

        recortar_video(f"{ruta_video}{filename}")
        
        os.environ["VIDEO_PATH_HEDRA"] = f"{ruta_video}{filename}"

    else:
        print("Error downloading video")

def enviar_avatar_request(text, avatar_image, aspect_ratio, prompt, use_manual_seed, seed, voice_id, access_token):

    # Genera una semilla aleatoria si no se proporciona y si use_manual_seed es False
    if not use_manual_seed:
        seed = random.randint(1000000, 9999999)  # Genera un número aleatorio de 7 dígitos

    url = "https://www.hedra.com/api/app/v1/app/avatars/predict-async"
    headers = {
        "Host": "www.hedra.com",
        "Connection": "keep-alive",
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    # Crear el cuerpo de la solicitud
    data = {
        "text": text,
        "avatar_image": avatar_image,
        "aspect_ratio": aspect_ratio,
        "avatar_image_input": {
            "prompt": prompt,
            "seed": seed
        },
        "audio_source": "tts",  # Usando TTS como la fuente de audio
        "voice_id": voice_id
    }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Verificar la respuesta
    if response.status_code == 200:
        print("Request successful!")
        #print(response.json())  # Imprimir respuesta si es JSON
        # Supongamos que tienes el siguiente diccionario
        responses = response.json()

        # Extraer el job_id
        job_id = responses['job_id']
        return job_id
    else:
        proceso_completo()
        time.sleep(2)
        access = os.environ.get("ACCESS_TOKEN_HEDRA")
        #if access:
        procesar_avatar_request(voice_id,use_manual_seed,seed,aspect_ratio,prompt,text)

def procesar_avatar_request(
    selected_voice_origen_id,
    use_manual_seed,
    seed,
    aspect_ratio,
    prompt_txt,
    text
):

    
    access_token = os.environ.get("ACCESS_TOKEN_HEDRA")
    # Convertir la imagen en Base64 desde la ruta
    try:
        with open("/tmp/avatar_img.jpg", "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró la imagen en la ruta '/tmp/avatar_img.jpg'")

    # Validación de los parámetros
    if not base64_string:
        raise ValueError("Se debe proporcionar una cadena Base64 para la imagen del avatar")
    if not access_token:
        raise ValueError("Se debe proporcionar un token de acceso válido")

    # Enviar solicitud con los datos
    job_id = enviar_avatar_request(
        text=text,
        avatar_image=base64_string,
        aspect_ratio=aspect_ratio,
        prompt=prompt_txt,
        use_manual_seed=use_manual_seed,
        seed=seed,
        voice_id=selected_voice_origen_id,
        access_token=access_token,
    )

    # Procesar la respuesta
    if job_id:
        resultado = obteneravatar(access_token)
        #print("Resultado de la solicitud:", resultado)
        project = resultado['projects'][0]
        initial_progress = project['progress']
        update_progress_bar(initial_progress, "/tmp/videos_tts/", access_token, job_id)

