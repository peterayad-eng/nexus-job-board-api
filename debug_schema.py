import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobboard.settings')
django.setup()

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema

# Patch to debug the issue
original_get_parameters = AutoSchema._get_parameters

def debug_get_parameters(self):
    try:
        return original_get_parameters(self)
    except AttributeError as e:
        print(f"ERROR in view: {self.view.__class__.__name__}")
        print(f"Method: {self.method}")
        print(f"Error: {e}")
        # Return empty parameters to continue
        return []

AutoSchema._get_parameters = debug_get_parameters

# Try to generate schema
try:
    generator = SchemaGenerator()
    schema = generator.get_schema()
    print("✅ Schema generation successful!")
except Exception as e:
    print(f"❌ Schema generation failed: {e}")

