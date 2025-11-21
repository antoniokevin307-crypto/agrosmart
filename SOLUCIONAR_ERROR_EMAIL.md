## 🆘 Error: "Error al enviar el email. Intenta nuevamente."

### 🔍 Causa del Problema

El error ocurre porque **EMAIL_HOST_USER y/o EMAIL_HOST_PASSWORD no están configurados** en el archivo `.env`.

### ✅ Solución Paso a Paso

#### **Paso 1: Editar el archivo `.env`**

Abre el archivo `.env` en la raíz del proyecto:
```
e:\Proyecto Programación III\agrosmart\.env
```

Busca estas líneas:
```env
EMAIL_HOST_USER=ejemplo@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

#### **Paso 2: Configurar tu Email de Gmail**

En `EMAIL_HOST_USER`, cambia `ejemplo@gmail.com` por tu email real:
```env
EMAIL_HOST_USER=tu_email_real@gmail.com
```

#### **Paso 3: Generar Contraseña de Aplicación**

**⚠️ IMPORTANTE: NO USES TU CONTRASEÑA NORMAL DE GMAIL**

Sigue estos pasos:

1. **Ve a https://myaccount.google.com**
2. Haz clic en **"Seguridad"** en el menú izquierdo
3. En "Cómo accedes a Google", busca **"Verificación en 2 pasos"**
4. Si aún NO ESTÁ habilitada:
   - Haz clic en **"Verificación en 2 pasos"**
   - Sigue las instrucciones (necesitarás tu número de teléfono)
   - Una vez terminado, vuelve a Seguridad

5. Ahora ve a **https://myaccount.google.com/apppasswords**
6. En el dropdown "Selecciona la app", elige: **Correo**
7. En el dropdown "Selecciona el dispositivo", elige: **Windows** (o tu SO)
8. Haz clic en **"Generar"**
9. Google mostrará una contraseña de 16 caracteres con espacios
   - Ejemplo: `xxxx xxxx xxxx xxxx`
10. **Cópiala exactamente (con los espacios)**

#### **Paso 4: Pegar Contraseña en .env**

En `EMAIL_HOST_PASSWORD`, pega esa contraseña:
```env
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

**Ejemplo completo:**
```env
EMAIL_HOST_USER=mi_email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

#### **Paso 5: Guardar y Reiniciar**

1. Guarda el archivo `.env`
2. En la terminal donde corre Django, presiona **Ctrl+C** para detener el servidor
3. Ejecuta nuevamente:
   ```bash
   python manage.py runserver
   ```

#### **Paso 6: Probar Envío de Email**

Ejecuta este comando para probar:
```bash
python test_email.py
```

Deberías ver:
```
✅ EMAIL ENVIADO EXITOSAMENTE
✉️  Se envió un email de prueba a: tu_email@gmail.com
```

Si ves esto, ¡está configurado correctamente!

### 🐛 Si Aún Hay Errores

#### **Error: "SMTPAuthenticationError"**
- Verifica que EMAIL_HOST_USER sea correcto
- Verifica que EMAIL_HOST_PASSWORD tenga exactamente 16 caracteres
- Espera 1-2 minutos después de generar la contraseña
- Intenta generar una nueva contraseña en Google

#### **Error: "SMTPNotSupportedError"**
- Verifica que `EMAIL_USE_TLS=True` en .env

#### **Error: "Invalid address"**
- El EMAIL_HOST_USER está vacío
- Asegúrate que dice `EMAIL_HOST_USER=tu_email@gmail.com` (NO `tu_email@gmail.com`)

#### **Error: "SMTPException"**
- Tu conexión a Internet puede estar bloqueando puerto 587
- Contacta a tu administrador de red

### ❓ ¿Por qué no puedo usar mi contraseña normal?

Google requiere una "Contraseña de Aplicación" especial por seguridad. Esto es así cuando tienes:
- ✅ Verificación en 2 pasos habilitada (recomendado)
- ✅ Una contraseña de app es más segura que compartir tu contraseña principal

### 🆓 Alternativa: Sin Verificación en 2 Pasos

Si NO quieres habilitar 2FA:

1. Ve a **https://myaccount.google.com/lesssecureapps**
2. Activa **"Permitir aplicaciones menos seguras"**
3. En `.env`, usa tu contraseña normal:
   ```env
   EMAIL_HOST_USER=mi_email@gmail.com
   EMAIL_HOST_PASSWORD=mi_contraseña_de_gmail
   ```

**⚠️ NO RECOMENDADO** - Es menos seguro.

### ✅ Verificar Configuración Correcta

Una vez configurado correctamente, cuando hagas clic en "Enviar Código" en la página de registro:

1. Deberías recibir un email en unos segundos
2. El email dice: "Código de verificación: 123456"
3. Ingresas ese código en la siguiente pantalla
4. ¡Listo! Tu cuenta está creada

---

**Consulta el README.md para más detalles: `e:\Proyecto Programación III\agrosmart\README.md`**
