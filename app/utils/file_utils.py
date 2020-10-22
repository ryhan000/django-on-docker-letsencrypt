from django.utils.text import slugify
import uuid
import os


def get_file_path(instance, filename):
    file_name, file_ext = os.path.splitext(filename)
    file_ext = file_ext.lower()
    filename = str(uuid.uuid4()) + file_ext
    path = slugify(instance.__class__.__name__)
    return os.path.join(path, filename.lower())
