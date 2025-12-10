import os
import sys
import django
from django.conf import settings

with open('debug_output.txt', 'w') as f:
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NoteCraft_backend.settings')
        django.setup()
        f.write(f"DEBUG: {settings.DEBUG}\n")
        f.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
