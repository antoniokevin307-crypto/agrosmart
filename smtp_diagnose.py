#!/usr/bin/env python
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

print('=== SMTP DIAGNOSTIC ===')
print('EMAIL_HOST:', EMAIL_HOST)
print('EMAIL_PORT:', EMAIL_PORT)
print('EMAIL_USE_TLS:', EMAIL_USE_TLS)
print('EMAIL_HOST_USER:', EMAIL_HOST_USER)
print('EMAIL_HOST_PASSWORD set:', bool(EMAIL_HOST_PASSWORD))
if EMAIL_HOST_PASSWORD:
    print('EMAIL_HOST_PASSWORD length:', len(EMAIL_HOST_PASSWORD))
    print('EMAIL_HOST_PASSWORD contains space:', ' ' in EMAIL_HOST_PASSWORD)

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    print('\nERROR: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD are not set. Edit your .env in the project root (same folder as manage.py).')
    raise SystemExit(1)

print('\nAttempting SMTP connection and login (debug output follows)...')

import smtplib

try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
    server.set_debuglevel(1)
    if EMAIL_USE_TLS:
        server.ehlo()
        server.starttls()
        server.ehlo()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    print('\nLOGIN OK')
    server.quit()
except Exception as e:
    print('\nERROR during SMTP connection/login:')
    traceback.print_exc()
    # If SMTP library exposed .smtp_code and .smtp_error, print them
    if hasattr(e, 'smtp_code'):
        print('smtp_code:', e.smtp_code)
    if hasattr(e, 'smtp_error'):
        print('smtp_error:', e.smtp_error)
    raise

print('\nDone')
