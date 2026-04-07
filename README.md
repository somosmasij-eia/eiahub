# EIA Hub — Plataforma de Transporte y Comunidad

EIA Hub es una aplicación web desarrollada con **Flask** para la comunidad de la Universidad EIA. Facilita la gestión de transporte (carpool y rutas) y fomenta la interacción entre los miembros de la institución.

## Características

- **Autenticación institucional**: Registro e inicio de sesión con correo `@eia.edu.co` mediante magic link (sin contraseña). Los emails se envían con Resend.
- **Gestión de rutas**: Visualización y registro en rutas de transporte universitario.
- **CarPool**: Mapa interactivo con Leaflet.js centrado en la Universidad EIA. (Próximamente: unirse a viajes compartidos.)
- **Dashboard personalizado**: Vista general para el usuario autenticado.
- **Conoce la U**: Sección de información del campus. (Próximamente: tour virtual.)

## Estructura del Proyecto

```
eia-hub/
├── app.py              # Punto de entrada y factory de la app
├── auth.py             # Registro, verificación y magic link
├── config.py           # Configuración por variables de entorno
├── models.py           # Base de datos: User y RegistroRuta (SQLAlchemy)
├── routes.py           # Rutas y lógica de negocio
├── Procfile            # Comando de arranque para Render
├── requirements.txt    # Dependencias del proyecto
├── .env.example        # Plantilla de variables de entorno
├── templates/          # Archivos HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── carpool.html
│   ├── transporte.html
│   ├── registro_ruta.html
│   └── conoce.html
└── static/             # CSS, JS e imágenes
```

## Requisitos

- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- resend
- python-dotenv
- gunicorn

## Instalación local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/eia-hub.git
   cd eia-hub
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` y completa los valores:

   | Variable | Descripción |
   |---|---|
   | `SECRET_KEY` | Clave secreta de Flask (cualquier texto largo y aleatorio) |
   | `RESEND_API_KEY` | API Key de [resend.com](https://resend.com) |
   | `RESEND_FROM` | Remitente de los emails (dejar el valor por defecto en desarrollo) |

5. Ejecuta la aplicación:
   ```bash
   python app.py
   ```
   Abre [http://localhost:5000](http://localhost:5000) en tu navegador.

## Despliegue en Render

1. Crea un **Web Service** en [render.com](https://render.com) conectado a este repositorio.
2. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "app:create_app()"`
3. Agrega las variables de entorno en el panel de Render:
   - `SECRET_KEY`
   - `RESEND_API_KEY`
   - `RESEND_FROM` → `EIA Hub <onboarding@resend.dev>`

## Flujo de autenticación

```
/auth/register  →  usuario ingresa nombre + correo @eia.edu.co
      ↓
Email con enlace de verificación (válido 30 min)
      ↓
/auth/verify/<token>  →  cuenta verificada
      ↓
/  (login)  →  usuario ingresa su correo
      ↓
Email con magic link (válido 30 min)
      ↓
/auth/magic/<token>  →  sesión iniciada → Dashboard
```

## Licencia

Proyecto académico e institucional — Universidad EIA.
