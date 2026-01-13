#!/usr/bin/env python
"""
Health check script for Django application
"""
import sys
import os

def check_health():
    try:
        # Importar Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        # Verificar conexão com banco de dados
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        print("✓ Health check passou: Aplicação saudável")
        return 0
    except Exception as e:
        print(f"✗ Health check falhou: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(check_health())
