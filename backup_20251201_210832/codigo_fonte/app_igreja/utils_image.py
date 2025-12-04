"""
Utilitários para processamento de imagens
"""
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def redimensionar_imagem(image_field, max_width=1920, max_height=1080, quality=85):
    """
    Redimensiona uma imagem mantendo a proporção e reduzindo o tamanho do arquivo.
    
    Args:
        image_field: Campo de imagem do Django (InMemoryUploadedFile ou UploadedFile)
        max_width: Largura máxima em pixels (padrão: 1920)
        max_height: Altura máxima em pixels (padrão: 1080)
        quality: Qualidade JPEG (0-100, padrão: 85)
    
    Returns:
        InMemoryUploadedFile redimensionado ou None se não houver imagem
    """
    if not image_field:
        return None
    
    try:
        # Abrir a imagem
        img = Image.open(image_field)
        
        # Converter para RGB se necessário (para JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Criar fundo branco para imagens com transparência
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Obter dimensões originais
        width, height = img.size
        
        # Calcular novas dimensões mantendo proporção
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Redimensionar
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Salvar em memória
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Criar novo arquivo InMemoryUploadedFile
        filename = image_field.name
        if not filename:
            filename = 'image.jpg'
        elif not filename.lower().endswith(('.jpg', '.jpeg')):
            # Garantir extensão .jpg
            filename = filename.rsplit('.', 1)[0] + '.jpg'
        
        return InMemoryUploadedFile(
            output,
            'ImageField',
            filename,
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    except Exception as e:
        # Se houver erro, retornar a imagem original
        print(f"Erro ao redimensionar imagem: {e}")
        return image_field

