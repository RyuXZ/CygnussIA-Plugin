import base64
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from config import MAX_RESOLUTION_4K, MAX_RESOLUTION_8K

def decode_b64(b64_string: str) -> Image.Image:
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]
    image_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(image_data)).convert("RGB")

def encode_b64(image: Image.Image, format: str = "PNG") -> str:
    buffered = BytesIO()
    image.save(buffered, format=format)
    encoded_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{encoded_str}"

def upscale_resolution(image: Image.Image, target: str, algorithm: str = "lanczos") -> Image.Image:
    """Aplica diferentes algoritmos de escalado según la solicitud."""
    width, height = image.size
    
    if target == "4K":
        scale_factor = min(MAX_RESOLUTION_4K[0] / width, MAX_RESOLUTION_4K[1] / height)
    elif target == "8K":
        scale_factor = min(MAX_RESOLUTION_8K[0] / width, MAX_RESOLUTION_8K[1] / height)
    else:
        scale_factor = 2.0
        
    new_size = (int(width * scale_factor), int(height * scale_factor))

    if algorithm == "lanczos":
        # Algoritmo tradicional, excelente para no distorsionar la imagen original
        return image.resize(new_size, Image.Resampling.LANCZOS)
    elif algorithm == "esrgan_simulation":
        # Aquí iría la llamada a un modelo de IA real como RealESRGAN
        # Simulamos el efecto con un escalado bicúbico + un filtro de enfoque
        resized = image.resize(new_size, Image.Resampling.BICUBIC)
        return resized.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    else:
        return image.resize(new_size, Image.Resampling.LANCZOS)

def optimize_textures(image: Image.Image, method: str = "frequency_separation") -> Image.Image:
    """
    Aplica algoritmos específicos para optimizar texturas (ropa, piel, renderizados 3D).
    """
    if method == "frequency_separation":
        # Conversión de PIL a OpenCV (numpy array)
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Algoritmo de mejora de texturas (Sharpening / High-pass filter simulation)
        # Excelente para resaltar micro-detalles en materiales complejos
        gaussian_blur = cv2.GaussianBlur(cv_img, (0, 0), 2.0)
        unsharp_image = cv2.addWeighted(cv_img, 1.5, gaussian_blur, -0.5, 0)
        
        # Devolver a formato PIL
        color_converted = cv2.cvtColor(unsharp_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(color_converted)
        
    elif method == "color_pop":
        # Algoritmo básico de saturación y contraste usando PIL puro
        enhancer = ImageEnhance.Color(image)
        img_colored = enhancer.enhance(1.2)
        enhancer_contrast = ImageEnhance.Contrast(img_colored)
        return enhancer_contrast.enhance(1.1)
        
    return image

def adjust_pose_structure(image: Image.Image, target_model: str = "openpose") -> Image.Image:
    """
    Prepara la imagen o la procesa utilizando modelos de estimación de pose.
    """
    if target_model == "openpose":
        # Aquí se integraría la conexión a una API de Stable Diffusion local + ControlNet
        # Como placeholder, convertimos la imagen a un mapa de bordes (simulando Canny/Lineart)
        # que es el primer paso antes de enviarlo a un modelo de alteración de pose.
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(cv_img, 100, 200)
        
        # Convertir de vuelta a RGB para Photoshop
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(edges_rgb)
        
    return image