from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


MAX_PROFILE_IMAGE_SIZE_MB = 5
MAX_PROFILE_IMAGE_WIDTH = 1024
MAX_PROFILE_IMAGE_HEIGHT = 1024
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']


def optimize_image(image, size=(256, 256)):
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
