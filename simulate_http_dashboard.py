#!/usr/bin/env python
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosmart.settings')
sys.path.insert(0, os.path.dirname(__file__))
import django
django.setup()
from django.test import Client
from django.conf import settings

# Durante la prueba añadimos hosts permitidos para evitar DisallowedHost
settings.ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']

c = Client()
email = 'test_local@example.com'
password = 'testpass123'
logged = c.login(email=email, password=password)
print('login ok?', logged)
resp = c.get('/dashboard/2/')
print('GET /dashboard/2/ status:', resp.status_code)
print('Resp length:', len(resp.content))
# Print small part of response to debug
print(resp.content[:1000])
