import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from docx import Document
from dotenv import load_dotenv
import mammoth
from email.utils import make_msgid

load_dotenv()

def convertir_docx_a_html(docx_path: str):
    """
    Convierte un archivo .docx a HTML utilizando la librería Mammoth.
    :param docx_path: Ruta del archivo .docx de entrada.
    :param html_output_path: Ruta donde se guardará el archivo .html de salida.
    """
    # Calcular el nombre del archivo de salida
    html_output_path = docx_path.replace(".docx", ".html")

    # Abrir el archivo docx
    with open(docx_path, "rb") as docx_file:
        # Usar Mammoth para convertir el archivo docx a HTML
        result = mammoth.convert_to_html(docx_file)

    # Obtener el contenido HTML resultante
    html_content = result.value  # El HTML generado por Mammoth

    # Reemplazar el formato de <table>
    html_content = html_content.replace(
        '<table>',
        '<table align="center" width="700" cellpadding="10" cellspacing="0" style="background-color: #ddddff; border-collapse: collapse; margin: 20px auto; font-family: Calibri, sans-serif; font-size: 18px; border-radius: 20px;">'
        )

    # Guardar el contenido HTML en el archivo de salida
    with open(html_output_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    return html_content

def obtener_imagenes_docx(docx_path: str):
    """
    Extrae las imágenes del archivo .docx y las convierte a base64.
    :param docx_path: Ruta del archivo .docx de entrada.
    :return: Diccionario de imágenes con el Content-ID como clave y los datos de la imagen como valor.
    """
    doc = Document(docx_path)
    imagenes = {}
    
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            content_id = make_msgid(domain="example.com")
            imagenes[content_id] = image_data

    return imagenes

def reemplazar_imagenes_en_html(html_content, imagenes):
    """
    Reemplaza las referencias a las imágenes en base64 en el HTML con los CID.
    :param html_content: El contenido HTML con las imágenes en base64.
    :param imagenes: Diccionario con el Content-ID de cada imagen y sus datos.
    :return: El HTML con las imágenes reemplazadas por los CID.
    """
    # Buscar todas las etiquetas <img> en el HTML
    img_tags = re.findall(r'<img [^>]*src="data:image[^"]+"[^>]*>', html_content)
    
    for idx, img_tag in enumerate(img_tags, 1):
        # Buscar el src (data:image...)
        src_match = re.search(r'src="(data:image[^"]+)"', img_tag)
        if src_match:
            base64_data = src_match.group(1)  # Obtener el string base64
            # Nombrar la imagen como image{idx}.png
            img_filename = f"image{idx}.png"
            # Obtener el CID correspondiente
            content_id = list(imagenes.keys())[idx - 1]  # Obtener el CID del diccionario
            # Reemplazar la referencia de la imagen en el HTML por el CID
            html_content = html_content.replace(base64_data, f"cid:{content_id}")
    
    return html_content

def enviar_correo_electronico(template_path:str, datos_campos:dict, datos_smtp:dict=None, asunto:str="", destinatarios:list=None, cc:list=None, cco:list=None, adjuntos:list=None):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"La plantilla {template_path} no existe.")

    # Extraer contenido y convertirlo a HTML
    html_content = convertir_docx_a_html(template_path)

    # Obtener las imágenes del archivo DOCX
    imagenes = obtener_imagenes_docx(template_path)

    # Reemplazar las imágenes en el HTML por las referencias CID
    html_content = reemplazar_imagenes_en_html(html_content, imagenes)

    # Reemplazar los marcadores con los valores de datos_campos
    for key, value in datos_campos.items():
        html_content = re.sub(r'{{' + re.escape(key) + r'}}', str(value), html_content)

    # Estructura HTML del correo
    email_html = f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
            {html_content}
        </body>
    </html>
    """

    # Crear el mensaje de correo
    msg = MIMEMultipart("related")
    msg['Subject'] = asunto
    msg['From'] = datos_smtp["email_from"]
    msg['To'] = ", ".join(destinatarios)
    if cc:
        msg['Cc'] = ", ".join(cc)
    if cco:
        msg['Bcc'] = ", ".join(cco)

    # Adjuntar el HTML al correo
    msg.attach(MIMEText(email_html, "html"))

    # Adjuntar las imágenes como inline (CID)
    for content_id, image_data in imagenes.items():
        img = MIMEImage(image_data)
        img.add_header("Content-ID", f"<{content_id}>")
        img.add_header("Content-Disposition", "inline", filename="image.png")  # Nombre genérico
        msg.attach(img)

    # Adjuntar otros archivos
    if adjuntos:
        for file_path in adjuntos:
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                    part["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
            else:
                print(f"Advertencia: El archivo adjunto {file_path} no existe.")

    # Enviar el correo
    resultado = None
    try:
        with smtplib.SMTP(
            datos_smtp["smtp_server"],
            datos_smtp["smtp_port"]
            ) as server:
            
            server.starttls()
            server.login(
                datos_smtp["email_user"],
                datos_smtp["email_password"]
            )
            server.send_message(msg)
            resultado = {"status": "success", "message": "Correo enviado con éxito."}
    except Exception as e:
        resultado = {"status": "error", "message": f"Error al enviar el correo: {e}"}
        raise Exception(f"Error al enviar el correo: {e}")
    
    return resultado


