import os
import subprocess
from PIL import Image
import gradio as gr
import cv2

# Codigo creado por IA(Sistema de Interes) https://www.youtube.com/@IA.Sistema.de.Interes
def run_commands_text_to_video(description, aspect_ratio, enhance_check, model, style, upscale_check, version, movement, task_type, img=None, is_extend=False, is_recreate=False):
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("Generating video: Text to Video...")
                commands.append(
                    f'python create_text_to_video.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}" --style "{style}" --aspect_ratio "{aspect_ratio}"'
                )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')


                print("Generating video: Text to Video...")
                commands.append(
                    f'python create_text_to_video.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}" --style "{style}" --aspect_ratio "{aspect_ratio}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")

            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("Generating video 1.5: Text to Video...")
                commands.append(
                    f'python create_text_to_video_15.py --prompt "{description}" --enhance {str(enhance_check).lower()} --style "{style}" --aspect_ratio "{aspect_ratio}" --resolution "512" --movement_amplitude "{movement}"'
                )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("Generating video 1.5: Text to Video...")
                commands.append(
                    f'python create_text_to_video_15.py --prompt "{description}" --enhance {str(enhance_check).lower()} --style "{style}" --aspect_ratio "{aspect_ratio}" --resolution "512" --movement_amplitude "{movement}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None




def run_commands_videotovideo(description, aspect_ratio, enhance_check, model, style, upscale_check, task_type, add_end_frame, version, movement, img=None, is_extend=False, is_recreate=False):
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                commands.append('python utils/video_fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')
                commands.append('python upload/file_uploader.py --file_info "file_info2" --image "img_fragmento2"')

                print("Generating video with headtailimg2video...")
                commands.append(
                     f'python headtailimg2video.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                commands.append('python utils/video_fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video with Image to Video...")
                commands.append(
                    f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")


            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                commands.append('python utils/video_fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')
                commands.append('python upload/file_uploader.py --file_info "file_info2" --image "img_fragmento2"')

                print("Generating video with headtailimg2video...")
                commands.append(
                    f'python create_image2_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                commands.append('python utils/video_fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video 1.5 with Image to Video...")
                commands.append(
                    f'python create_image_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None





def run_commands_re_create(description, aspect_ratio, enhance_check, model, style, upscale_check, task_type, add_end_frame, version, movement, img=None, is_extend=False, is_recreate=False):
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if True:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video with Image to Video...")
                commands.append(
                    f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")

            if True:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video 1.5 with Image to Video...")
                commands.append(
                    f'python create_image_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None

def run_commands_extend(description, aspect_ratio, enhance_check, model, style, upscale_check, task_type, add_end_frame, version, movement, img=None, is_extend=False, is_recreate=False):
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if True:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("Last frame...")
                commands.append('python utils/fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video with Image to Video...")
                commands.append(
                    f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")

            if True:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("Last frame...")
                commands.append('python utils/fragment.py')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video 1.5 with Image to Video...")
                commands.append(
                    f'python create_image_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None


def run_commands_reference(description, aspect_ratio, enhance_check, model, style, upscale_check, task_type, add_end_frame, version, movement, aspect_ratios, img=None, is_extend=False, is_recreate=False):
    print(aspect_ratios)
    print(movement)
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                if task_type == "headtailimg2video":
                    print("Generating video with Image to Video...")
                    """commands.append(
                        f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                    )"""
                    commands.append(
                        f'python create_video_reference.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                    )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                if task_type == "headtailimg2video":
                    print("Generating video with Image to Video...")
                    """commands.append(
                        f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                    )"""
                    commands.append(
                        f'python create_video_reference.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                    )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")


            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')
                commands.append('python upload/file_uploader.py --file_info "file_info2" --image "img_fragmento2"')

                if task_type == "headtailimg2video":
                    print("Generating video with headtailimg2video...")
                    commands.append(
                        f'python create_video_reference2_15.py --text "{description}" --resolution "512" --movement_amplitude "{movement}" --enhance {str(enhance_check).lower()} --aspect_ratio "{aspect_ratios}"'
                    )


                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                if task_type == "headtailimg2video":
                    print("Generating video 1.5 with Image to Video...")
                    commands.append(
                        f'python create_video_reference_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}" --aspect_ratio "{aspect_ratios}"'
                    )
                    

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None


def run_commands_dual2(description, aspect_ratio, enhance_check, model, style, upscale_check, task_type, add_end_frame, version, movement, img=None, is_extend=False, is_recreate=False):
    try:
        # Verifica si la versión es "1.0"
        if version == "1.0":
            commands = []

            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')
                commands.append('python upload/file_uploader.py --file_info "file_info2" --image "img_fragmento2"')

                if task_type == "headtailimg2video":
                    print("Generating video with headtailimg2video...")
                    commands.append(
                        f'python headtailimg2video.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                    )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video with Image to Video...")
                commands.append(
                    f'python create_task.py --prompt "{description}" --enhance {str(enhance_check).lower()} --model "{model}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')

            # Ejecutar todos los comandos
            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path
        
        else:
            # Si la versión no es "1.0", ejecutamos un bloque similar para edición o ajuste
            commands = []
            
            # Los mismos comandos, pero ajustados o editados para la versión que no es "1.0"
            print("Executing in 1.5 version...")


            if add_end_frame:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')
                commands.append('python upload/file_uploader.py --file_info "file_info2" --image "img_fragmento2"')

                print("Generating video with headtailimg2video...")
                commands.append(
                    f'python create_image2_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )
                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            else:
                # Comandos generales según el tipo de tarea
                if upscale_check:
                    commands.append('python vidu_credit.py --credit 4')
                else:
                    commands.append('python vidu_credit.py --credit 0')

                print("File  Uploader...")
                commands.append('python upload/file_uploader.py --file_info "file_info" --image "img_fragmento"')

                print("Generating video 1.5 with Image to Video...")
                commands.append(
                    f'python create_image_to_video_15.py --text "{description}" --enhance {str(enhance_check).lower()} --resolution "512" --movement_amplitude "{movement}"'
                )

                print("Video in progress...")
                commands.append('python utils/process_task.py')

                if upscale_check:
                    print("Generate Upscale...")
                    commands.append('python utils/upscale_task.py')
                    print("Upscale in progress...")
                    commands.append('python utils/process_task_upscale.py')
                    commands.append('python utils/delete_task.py')
                    commands.append('python utils/delete_task_upscale.py')
                else:
                    commands.append('python utils/delete_task.py')
            

            output = ""
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output += f"Exit:\n{result.stdout}\n"
                print(result.stdout)

            video_path = "video.mp4"
            return output, video_path

    except Exception as e:
        return f"Excepción: {str(e)}", None



# Función para procesar y guardar la imagen automáticamente en formato JPG
def process_and_save_image(image, coordinates_file_path="/tmp/coordinates.txt"):
    jpg_path = "/tmp/img_fragmento.jpg"

    try:
        if image.format != "JPEG":
            image = image.convert("RGB")
        image.save(jpg_path, "JPEG", quality=100)
        if os.path.exists(jpg_path):
            print(f"Imagen guardada correctamente")

            # Obtener las dimensiones de la imagen
            width, height = image.size

            # Guardar las coordenadas en un archivo de texto
            with open(coordinates_file_path, "w") as file:
                file.write(f"X: {width}\n")
                file.write(f"Y: {height}\n")

            print(f"Coordenadas guardadas correctamente")

        return None
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None

# Función para procesar y guardar la imagen automáticamente en formato JPG
def process_and_save_image1(image, coordinates_file_path="/tmp/coordinates.txt"):
    jpg_path = "/tmp/img_fragmento.jpg"

    try:
        if image.format != "JPEG":
            image = image.convert("RGB")
        image.save(jpg_path, "JPEG", quality=100)
        if os.path.exists(jpg_path):
            print(f"Imagen guardada correctamente")

            # Obtener las dimensiones de la imagen
            width, height = image.size

            # Guardar las coordenadas en un archivo de texto
            with open(coordinates_file_path, "w") as file:
                file.write(f"X: {width}\n")
                file.write(f"Y: {height}\n")

            print(f"Coordenadas guardadas correctamente")

        return None
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None

# Función para procesar y guardar la imagen automáticamente en formato JPG
def process_and_save_image2(image, coordinates_file_path="/tmp/coordinates2.txt"):
    jpg_path = "/tmp/img_fragmento2.jpg"

    try:
        if image.format != "JPEG":
            image = image.convert("RGB")
        image.save(jpg_path, "JPEG", quality=100)
        if os.path.exists(jpg_path):
            print(f"Imagen guardada correctamente")

            # Obtener las dimensiones de la imagen
            width, height = image.size

            # Guardar las coordenadas en un archivo de texto
            with open(coordinates_file_path, "w") as file:
                file.write(f"X: {width}\n")
                file.write(f"Y: {height}\n")

            print(f"Coordenadas guardadas correctamente")
    
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")



# Función para obtener el último frame de un video
def get_last_frame(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
        ret, frame = cap.read()
        cap.release()

        if ret:
            return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            print(f"Error al leer el último frame del video: {video_path}")
            return None
    except Exception as e:
        print(f"Excepción al obtener el último frame: {str(e)}")
        return None


# Función para ejecutar los comandos de guardado
def run_save_commands():
    try:
        print("Rendering video...")
        commands = [
            "python utils/fragment.py",
            "python utils/union.py"
        ]
        output = ""
        for command in commands:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output += f"Exit:\n{result.stdout}\n"
            print(result.stdout)
        video_path = "video.mp4"
        return output, video_path
    except Exception as e:
        return f"Excepción al guardar: {str(e)}", None

# Función para mostrar o ocultar el segundo cuadro de imagen
def activar_end_frame(activar):
    return gr.update(visible=activar)
   
def toggle_dropdowns(version):
    # Si la versión es "1.0", muestra el dropdown del modelo
    model_visibility = gr.update(visible=True) if version == "1.0" else gr.update(visible=False)
    # Si la versión es "1.0" o "1.5", muestra el dropdown de "Movement Amplitude"
    movement_amplitude_visibility = gr.update(visible=True) if version == "1.5" else gr.update(visible=False)
    return model_visibility, movement_amplitude_visibility

def toggle_dropdowns2(version):
    # Si la versión es "1.0", muestra el dropdown del modelo
    model_visibility = gr.update(visible=True) if version == "1.0" else gr.update(visible=False)

    add_end_frame = gr.update(visible=True) if version == "1.5" else gr.update(visible=False)

    aspect_ratio_visibility = gr.update(visible=True) if version == "1.5" else gr.update(visible=False)
    # Si la versión es "1.0" o "1.5", muestra el dropdown de "Movement Amplitude"
    movement_amplitude_visibility = gr.update(visible=True) if version == "1.5" else gr.update(visible=False)
    return model_visibility, movement_amplitude_visibility, add_end_frame, aspect_ratio_visibility

# Definir la interfaz
with gr.Blocks() as demo:
    # Agregar un título en grande al inicio de la interfaz
    gr.HTML(f"<h1 style='text-align: center; font-size: 3em;'>VIDU STUDIO 3.0 - AUTOMATIC</p>Created by:<a href='https://www.youtube.com/@IA.Sistema.de.Interes' target='_blank'>IA(Sistema de Interés)</a></p>")
    with gr.Tabs():
        # Primera pestaña: Image to Video
        with gr.Tab("Image to Video"):
            with gr.Row():
                with gr.Column():
                    version_dropdown3 = gr.Dropdown(
                        choices=["1.0", "1.5"],
                        label="Versión",
                        value="1.0",
                        elem_id="version_dropdown3"
                    )
                    add_end_frame = gr.Checkbox(label="Add End Frame", value=False)

                    # Fila para mostrar ambas imágenes cuando se activa
                    with gr.Row():
                         # Imagen de inicio (carga de archivo)
                        img1 = gr.Image(type="pil", label="Drag image here or select image", interactive=True,
                    elem_id="img1", width=200, height=200)  # Ajustar tamaño de la imagen

                        # Imagen de fin (se oculta inicialmente)
                        img2 = gr.Image(type="pil", label="Upload the last frame image", interactive=True,
                    elem_id="img2", visible=False, width=200, height=200)  # Ajustar tamaño de la imagen

                    description_input = gr.Textbox(label="Prompt",
                                                   placeholder="Aquí va una caja de texto editable para el prompt",
                                                   elem_id="description_input")

                    enhance_checkbox = gr.Checkbox(label="Enhance prompt", value=False, elem_id="enhance_checkbox")

                    movement_amplitude_dropdown = gr.Dropdown(
                        choices=["auto", "small", "medium", "large"],
                        label="Movement Amplitude",
                        value="auto",
                        elem_id="movement_amplitude_dropdown",
                        visible=False
                    )

                    model_dropdown = gr.Dropdown(
                        choices=["vidu-1", "vidu-high-performance"],
                        label="Model",
                        value="vidu-1",
                        elem_id="model_dropdown",
                        visible=True
                    )
                    upscale_checkbox = gr.Checkbox(label="Upscale", value=False, elem_id="upscale_checkbox")
                    create_button = gr.Button("Create", elem_id="create_button")
                    extend_button = gr.Button("Extend", elem_id="extend_button")
                    recreate_button = gr.Button("Re-create", elem_id="recreate_button")  # Nuevo botón "Re-create"
                    save_button = gr.Button("Save", elem_id="save_button") # Botón de guardado

                with gr.Column():
                    video_output = gr.Video(label="Video Output Image to Video", height=400, elem_id="video_output_image_to_video")
                    output_textbox = gr.Textbox(label="Output", interactive=False, elem_id="output_textbox") # Cambia el nombre del textbox


            # Lógica para mostrar el segundo cuadro de imagen al activar el checkbox
            add_end_frame.change(activar_end_frame, add_end_frame, img2)

            # Procesar la imagen automáticamente cuando se carga
            img1.change(
                fn=process_and_save_image1,
                inputs=img1,
                outputs=[]
            )

            img2.change(
                fn=process_and_save_image2,
                inputs=img2,
                outputs=[]
            )

            # Botón "Create" y su salida
            create_button.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_dual2(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input, enhance_checkbox, model_dropdown, upscale_checkbox, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox, video_output]
            )

            # Botón "Extend" y su salida
            extend_button.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_extend(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input, enhance_checkbox, model_dropdown, upscale_checkbox, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox, video_output]
            )

            # Botón "Re-create" y su salida
            recreate_button.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_re_create(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input, enhance_checkbox, model_dropdown, upscale_checkbox, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox, video_output]
            )

            # Botón "Save" y su salida
            save_button.click(
                fn=run_save_commands,
                inputs=[],
                outputs=[output_textbox, video_output]
            )

            version_dropdown3.change(
                toggle_dropdowns, 
                inputs=version_dropdown3, 
                outputs=[model_dropdown, movement_amplitude_dropdown]
            )

        # Segunda pestaña: Reference to Video
        with gr.Tab("Reference to Video"):
            with gr.Row():
                with gr.Column():
                    version_dropdown3 = gr.Dropdown(
                        choices=["1.0", "1.5"],
                        label="Versión",
                        value="1.0",
                        elem_id="version_dropdown3"
                    )
                    add_end_frame = gr.Checkbox(label="Add End Frame", value=False, visible=False)

                    # Fila para mostrar ambas imágenes cuando se activa
                    with gr.Row():
                         # Imagen de inicio (carga de archivo)
                        img1 = gr.Image(type="pil", label="Drag image here or select image", interactive=True,
                    elem_id="img1", width=200, height=200)  # Ajustar tamaño de la imagen

                        # Imagen de fin (se oculta inicialmente)
                        img2 = gr.Image(type="pil", label="Upload the last frame image", interactive=True,
                    elem_id="img2", visible=False, width=200, height=200)  # Ajustar tamaño de la imagen


                    """image_input2 = gr.Image(type="pil", label="Drag image here or select image", interactive=True,
                                            elem_id="image_input2")"""

                    description_input2 = gr.Textbox(label="Prompt",
                                                    placeholder="Enter text to begin creating a video that aligns with the subject of the image",
                                                    elem_id="description_input2")

                    enhance_checkbox2 = gr.Checkbox(label="Enhance prompt", value=False, elem_id="enhance_checkbox2")

                    movement_amplitude_dropdown = gr.Dropdown(
                        choices=["auto", "small", "medium", "large"],
                        label="Movement Amplitude",
                        value="auto",
                        elem_id="movement_amplitude_dropdown",
                        visible=False
                    )

                    model_dropdown2 = gr.Dropdown(
                        choices=["vidu-1", "vidu-high-performance"],
                        label="Model",
                        value="vidu-1",
                        elem_id="model_dropdown2",
                        visible=True
                    )

                    aspect_ratio_dropdown = gr.Dropdown(
                        choices=["16:9", "9:16", "4:3", "1:1"],
                        label="Aspect Ratio",
                        value="16:9",
                        elem_id="aspect_ratio_dropdown",
                        visible=False
                    )

                    upscale_checkbox2 = gr.Checkbox(label="Upscale", value=False, elem_id="upscale_checkbox2")
                    create_button2 = gr.Button("Create", elem_id="create_button2")
                    extend_button2 = gr.Button("Extend", elem_id="extend_button2")
                    recreate_button2 = gr.Button("Re-create", elem_id="recreate_button2")  # Nuevo botón "Re-create"
                    save_button2 = gr.Button("Save", elem_id="save_button2") # Botón de guardado

                with gr.Column():
                    video_output2 = gr.Video(label="Video Output Reference to Video", height=400, elem_id="video_output_reference_to_video")
                    output_textbox2 = gr.Textbox(label="Output", interactive=False, elem_id="output_textbox2") # Cambia el nombre del textbox

            # Lógica para mostrar el segundo cuadro de imagen al activar el checkbox
            add_end_frame.change(activar_end_frame, add_end_frame, img2)

            img1.change(
                fn=process_and_save_image1,
                inputs=img1,
                outputs=[]
            )

            img2.change(
                fn=process_and_save_image2,
                inputs=img2,
                outputs=[]
            )


            create_button2.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement, aspect_ratios: run_commands_reference(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement, aspect_ratios=aspect_ratios),
                inputs=[description_input2, enhance_checkbox2, model_dropdown2, upscale_checkbox2, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown, aspect_ratio_dropdown],
                outputs=[output_textbox2, video_output2]
            )


            # Botón "Extend" y su salida
            extend_button2.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_extend(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input2, enhance_checkbox2, model_dropdown2, upscale_checkbox2, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox2, video_output2]
            )

            # Botón "Re-create" y su salida
            recreate_button2.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_re_create(desc, "16:9", enhance, model, "general", upscale, task_type="headtailimg2video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input2, enhance_checkbox2, model_dropdown2, upscale_checkbox2, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox2, video_output2]
            )

            # Botón "Save" y su salida
            save_button2.click(
                fn=run_save_commands,
                inputs=[],
                outputs=[output_textbox2, video_output2]
            )

            version_dropdown3.change(
                toggle_dropdowns2, 
                inputs=version_dropdown3, 
                outputs=[model_dropdown2, movement_amplitude_dropdown, add_end_frame, aspect_ratio_dropdown]
            )

        # Tercera pestaña: Text to Video
        with gr.Tab("Text to Video"):
            with gr.Row():
                with gr.Column():
                    version_dropdown3 = gr.Dropdown(
                        choices=["1.0", "1.5"],
                        label="Versión",
                        value="1.0",
                        elem_id="version_dropdown3"
                    )
                    description_input3 = gr.Textbox(label="Prompt",
                                                    placeholder="Enter text to begin creating a video",
                                                    elem_id="description_input3")
                    
                    enhance_checkbox3 = gr.Checkbox(label="Enhance prompt", value=False, elem_id="enhance_checkbox3")

                    aspect_ratio_dropdown = gr.Dropdown(
                        choices=["16:9", "9:16", "4:3", "1:1"],
                        label="Aspect Ratio",
                        value="16:9",
                        elem_id="aspect_ratio_dropdown"
                    )


                    movement_amplitude_dropdown = gr.Dropdown(
                        choices=["auto", "small", "medium", "large"],
                        label="Movement Amplitude",
                        value="auto",
                        elem_id="movement_amplitude_dropdown",
                        visible=False
                    )

                    model_dropdown3 = gr.Dropdown(
                        choices=["vidu-1", "vidu-high-performance"],
                        label="Model",
                        value="vidu-1",
                        elem_id="model_dropdown3",
                        visible=True  # Por defecto visible si se selecciona "1.0"
                    )
                    style_dropdown3 = gr.Dropdown(
                        choices=["general", "anime"],
                        label="Style",
                        value="general",
                        elem_id="style_dropdown3"
                    )

                    img1 = gr.Image(type="pil", label="Drag image here or select image", interactive=True,
                    elem_id="img1", width=200, height=200, visible=False)  # Ajustar tamaño de la imagen

                    add_end_frame = gr.Checkbox(label="Add End Frame", value=False, visible=False)

                    upscale_checkbox3 = gr.Checkbox(label="Upscale", value=False, elem_id="upscale_checkbox3")
                    create_button3 = gr.Button("Create", elem_id="create_button3")
                    extend_button3 = gr.Button("Extend", elem_id="extend_button3")
                    recreate_button3 = gr.Button("Re-create", elem_id="recreate_button3")  # Nuevo botón "Re-create"
                    save_button3 = gr.Button("Save", elem_id="save_button3") # Botón de guardado

                with gr.Column():
                    video_output3 = gr.Video(label="Video Output Text to Video", height=400, elem_id="video_output_text_to_video")
                    output_textbox3 = gr.Textbox(label="Output", interactive=False, elem_id="output_textbox3") # Cambia el nombre del textbox

            # Botón "Create" y su salida
            create_button3.click(
                fn=lambda desc, ratio, enhance, model, style, upscale, version, movement: run_commands_text_to_video(desc, ratio, enhance, model, style,
                                                                                     upscale, version, movement, task_type="text_to_video"),
                inputs=[description_input3, aspect_ratio_dropdown, enhance_checkbox3, model_dropdown3, style_dropdown3,
                        upscale_checkbox3, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox3, video_output3]
            )

    
            extend_button3.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_extend(desc, "16:9", enhance, model, "general", upscale, task_type="Extend", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input3, enhance_checkbox3, model_dropdown3, upscale_checkbox3, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox3, video_output3]
            )

            # Botón "Re-create" y su salida
            recreate_button3.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_re_create(desc, "16:9", enhance, model, "general", upscale, task_type="Re-create", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input3, enhance_checkbox3, model_dropdown3, upscale_checkbox3, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox3, video_output3]
            )


            # Botón "Save" y su salida
            save_button3.click(
                fn=run_save_commands,
                inputs=[],
                outputs=[output_textbox3, video_output3]
            )

            version_dropdown3.change(
                toggle_dropdowns, 
                inputs=version_dropdown3, 
                outputs=[model_dropdown3, movement_amplitude_dropdown]
            )



        # Cuarta pestaña: Video to Video
        with gr.Tab("Video to Video"):
            with gr.Row():
                with gr.Column():
                    version_dropdown3 = gr.Dropdown(
                        choices=["1.0", "1.5"],
                        label="Versión",
                        value="1.0",
                        elem_id="version_dropdown3"
                    )
                    video_input4 = gr.Video(label="Input Video", height=400, interactive=True)  # Agregar entrada de video

                    description_input4 = gr.Textbox(label="Prompt",
                                                    placeholder="Enter text to begin creating a video",
                                                    elem_id="description_input4")
                    enhance_checkbox4 = gr.Checkbox(label="Enhance prompt", value=False, elem_id="enhance_checkbox4")

                    aspect_ratio_dropdown = gr.Dropdown(
                        choices=["16:9", "9:16", "4:3", "1:1"],
                        label="Aspect Ratio",
                        value="16:9",
                        elem_id="aspect_ratio_dropdown",
                        visible=False
                    )


                    movement_amplitude_dropdown = gr.Dropdown(
                        choices=["auto", "small", "medium", "large"],
                        label="Movement Amplitude",
                        value="auto",
                        elem_id="movement_amplitude_dropdown",
                        visible=False
                    )

                    model_dropdown4 = gr.Dropdown(
                        choices=["vidu-1", "vidu-high-performance"],
                        label="Model",
                        value="vidu-1",
                        elem_id="model_dropdown4"
                    )

                    img1 = gr.Image(type="pil", label="Drag image here or select image", interactive=True,
                    elem_id="img1", width=200, height=200, visible=False)  # Ajustar tamaño de la imagen

                    img2 = gr.Image(type="pil", label="Upload the last frame image", interactive=True,
                    elem_id="img2", visible=False, width=200, height=200)  # Ajustar tamaño de la imagen

                    add_end_frame = gr.Checkbox(label="Add End Frame", value=False, visible=False)

                    upscale_checkbox4 = gr.Checkbox(label="Upscale", value=False, elem_id="upscale_checkbox4")
                    create_button4 = gr.Button("Create", elem_id="create_button4")
                    extend_button4 = gr.Button("Extend", elem_id="extend_button4")
                    recreate_button4 = gr.Button("Re-create", elem_id="recreate_button4")  # Nuevo botón "Re-create"
                    save_button4 = gr.Button("Save", elem_id="save_button4") # Botón de guardado

                with gr.Column():
                    video_output4 = gr.Video(label="Video Output Video to Video", height=400, elem_id="video_output_video_to_video")
                    output_textbox4 = gr.Textbox(label="Output", interactive=False, elem_id="output_textbox4") # Cambia el nombre del textbox

            # Guardar el video cargado en video.mp4
            def save_uploaded_video(video):
                if video is not None:
                    video_path = video
                    result = subprocess.run(f"cp '{video_path}' videotovideo.mp4", shell=True)
                    print(f"Video guardado en videotovideo.mp4")
                    print(result.stdout)

            # Ejecutar save_uploaded_video cuando se carga un video
            video_input4.upload(
                fn=save_uploaded_video,
                inputs=video_input4,
                outputs=None
            )

            # Botón "Create" y su salida
            create_button4.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_videotovideo(desc, "16:9", enhance, model, "general", upscale, task_type="video_to_video", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input4, enhance_checkbox4, model_dropdown4, upscale_checkbox4, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox4, video_output4]
            )
            
            # Botón "Extend" y su salida
            extend_button4.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_extend(desc, "16:9", enhance, model, "general", upscale, task_type="Extend", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input4, enhance_checkbox4, model_dropdown4, upscale_checkbox4, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox4, video_output4]
            )

            # Botón "Re-create" y su salida
            recreate_button4.click(
                fn=lambda desc, enhance, model, upscale, img, add_end, version, movement: run_commands_re_create(desc, "16:9", enhance, model, "general", upscale, task_type="Re-create", img=img, add_end_frame=add_end, version=version, movement=movement),
                inputs=[description_input4, enhance_checkbox4, model_dropdown4, upscale_checkbox4, img1, add_end_frame, version_dropdown3, movement_amplitude_dropdown],
                outputs=[output_textbox4, video_output4]
            )

            # Botón "Save" y su salida
            save_button4.click(
                fn=run_save_commands,
                inputs=[],
                outputs=[output_textbox4, video_output4]
            )

            version_dropdown3.change(
                toggle_dropdowns, 
                inputs=version_dropdown3, 
                outputs=[model_dropdown4, movement_amplitude_dropdown]
            )


# Ejecutar la interfaz
demo.launch(inline=False, debug=True, share=True)