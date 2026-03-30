import os 
from django.core.exceptions import ValidationError


def validate_resume_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Only PDF, DOC, and DOCX files are allowed.')

def validate_file_size(value):
    filesize = value.size
    if filesize > 2 * 1024 * 1024: # 5 MB is the limit
        raise ValidationError('File size must be less than 2MB')