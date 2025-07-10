from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.text import slugify


MAX_PROFILE_IMAGE_SIZE_MB = 5
MAX_PROFILE_IMAGE_WIDTH = 1024
MAX_PROFILE_IMAGE_HEIGHT = 1024
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']


def optimize_image(image, size=(256, 256)):
    """
    MEH: Optimize and Resize image for SEO base performance and volume of data
    """
    img = Image.open(image)
    img = img.convert('RGB')
    img_ratio = img.width / img.height
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
    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=75)
    buffer.seek(0)
    filename = image.name.split('.', 1)[0]+ '.webp'
    return ContentFile(buffer.read(), name=filename)


def safe_slug(value):
    """
    MEH: Keeps Farsi characters and replaces unsafe characters for filenames and paths
    """
    value = str(value).strip()
    # MEH: Replace spaces with dashes, remove unsafe characters except Farsi and dashes
    return ''.join(char if char.isalnum() or char in ' -_–—' or '\u0600' <= char <= '\u06FF' else '-' for char in value).replace(' ', '-')

