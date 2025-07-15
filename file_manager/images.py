from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os
import uuid
from django.core.files.base import ContentFile

ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP', 'JPG']


def optimize_image(image, size=(256, 256)):
    """
    MEH: Optimize and Resize image for SEO base performance and volume of data
    Export in webp format
    """
    img = Image.open(image).convert('RGB')
    img_ratio = img.width / img.height
    if size[0] and size[1]:
        target_ratio = size[0] / size[1]
        if img_ratio > target_ratio: # MEH: Crop Wider image: crop sides
            new_width = int(target_ratio * img.height)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else: # MEH: Taller image: crop top/bottom
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
        img = img.resize(size, Image.Resampling.LANCZOS)
    else:
        img = img.resize((img.width, img.height), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=75)
    buffer.seek(0)
    filename = image.name.split('.', 1)[0]+ '.webp'
    return ContentFile(buffer.read(), name=filename)


def create_square_thumbnail(image, size=(256, 256), background_color=(255, 255, 255)):
    img = Image.open(image).convert('RGBA')
    img.thumbnail(size, Image.LANCZOS)
    background = Image.new('RGBA', size, background_color + (255,)) # MEH: Create background and paste image onto it (centered)
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    background.paste(img, offset, mask=img)
    final_image = background.convert('RGB') # MEH: Convert to RGB (drop alpha) and save
    buffer = BytesIO()
    final_image.save(buffer, format='WEBP', quality=75)
    return ContentFile(buffer.getvalue(), name='thumb.webp')


def safe_slug(value, max_length=78):
    """
    MEH: Keeps Farsi characters and replaces unsafe characters for filenames and paths
    Replace spaces with dashes, remove unsafe characters except Farsi and dashes
    """
    value = str(value).strip()
    slug = ''.join(char if char.isalnum() or char in ' -_–—' or '\u0600' <= char <= '\u06FF' else '-' for char in value).replace(' ', '-')
    return slug[:max_length]
