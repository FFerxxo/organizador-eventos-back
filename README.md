# Organizador de Eventos - Backend

API del proyecto Organizador de Eventos Independientes (Equipo 6). Está hecha con Django REST Framework y guarda los datos en una base PostgreSQL en Supabase.

| | URL |
| --- | --- |
| Aplicación (frontend) | https://eventflow-front-two.vercel.app |
| API | https://eventflow-back.onrender.com |
| Estado de la API | https://eventflow-back.onrender.com/api/health/ |
| Documentación (Swagger) | https://eventflow-back.onrender.com/api/docs/ |
| Repositorio del frontend | https://github.com/FFerxxo/organizador-eventos-front |

> La API está en el plan gratuito de Render: si lleva un rato sin uso, la primera petición puede tardar hasta un minuto mientras el servicio despierta. Abrir primero `/api/health/` y esperar a que responda.

## Cuenta demo para la evaluación

| Correo | Contraseña |
| --- | --- |
| `demo@eventflow.com` | `demo1234` |

La cuenta trae tres eventos con fechas calculadas desde el día en que se preparó la demo:

- **Boda de Laura y Andrés**: gestiones vencidas, para hoy y próximas; dos hechas y una pospuesta con nota.
- **Lanzamiento Café Origen**: mañana está lleno justo hasta el límite de 6 h, para probar el conflicto de sobrecarga.
- **Cumpleaños de Sofía**: todas las gestiones hechas, el evento está al 100 %.

Para dejarla como nueva (por ejemplo el día de la revisión, para que las fechas queden alrededor de hoy):

```bash
python manage.py crear_demo
```

El comando es seguro de repetir: borra solo los eventos de la cuenta demo y los vuelve a crear. Se corre en local, con `DATABASE_URL` del `.env` apuntando a Supabase. No hace falta correrlo en Render. Solo toca la cuenta demo, no recibe otro correo.

## Cómo probar T1 a T4 con la cuenta demo

1. **Login**: entrar en la aplicación con la cuenta demo. Sin sesión, `/hoy`, `/crear`, `/evento/:id` y `/progreso` llevan a `/login`.
2. **T1 Crear evento**: en `/crear`, crear un evento y agregarle gestiones con fecha y horas. Queda guardado (`POST /api/eventos/` y `POST /api/eventos/<id>/subtareas/`).
3. **T2 Hoy**: en `/hoy` aparecen las gestiones agrupadas en vencidas, para hoy y próximas, con la regla de orden visible. Las hechas no salen; la pospuesta sale en su nueva fecha con su nota.
4. **T3 Reprogramar y conflicto**: en *Boda de Laura y Andrés*, reprogramar **Decoración floral** (3 h) para mañana. La aplicación avisa *"Quedarías con 9h planificadas (límite 6h)"* y ofrece moverla a otra fecha sugerida, bajar las horas o posponerla.
5. **T4 Hechas y progreso**: marcar una gestión como hecha o posponerla con una nota. La barra del evento y `/progreso` se actualizan, y la gestión sale de la carga del día en `/hoy`.

## Correrlo en local

Se necesita Python 3.10 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Queda en http://127.0.0.1:8000 y la documentación en http://127.0.0.1:8000/api/docs/.

Las tablas ya existen en Supabase, por eso el proyecto no tiene migraciones propias. Sin `DATABASE_URL` arranca con una base SQLite vacía: sirve para ver la documentación, pero no para guardar datos.

## Variables de entorno

Van en un archivo `.env` en la raíz (no se sube al repo) o en el panel de Render.

| Variable | Para qué |
| --- | --- |
| `SECRET_KEY` | Llave con la que se firman los tokens de sesión. |
| `DEBUG` | `True` solo en local. En Render va en `False`. |
| `DATABASE_URL` | Conexión a la base de Supabase. |
| `ALLOWED_HOSTS` | Direcciones del backend, separadas por coma y sin `https://`. Ej.: `eventflow-back.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | Sitios que pueden llamar a la API, separados por coma y con `https://`. Ej.: `https://eventflow-front-two.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Igual que la anterior. |

## Despliegue en Render

| Campo | Valor |
| --- | --- |
| Tipo | Web Service, Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn config.wsgi:application` |
| Health check path | `/api/health/` |

Cada merge a `main` se despliega solo. Después de desplegar, `/api/health/` debe responder `"base_de_datos": "ok"`; si dice `"sin conexión"`, revisar `DATABASE_URL`.

## Pruebas

```bash
python manage.py test
```

Corren sobre una base temporal, no tocan la de Supabase. Cubren login y registro, aislamiento entre organizadores, la vista Hoy y sus filtros, el límite diario, el conflicto de sobrecarga y su resolución, hechas y pospuestas, el progreso, los errores en JSON y la cuenta demo.

## Endpoints

El detalle de cada uno, con ejemplos, está en Swagger. Todos menos `health`, `registro` y `login` piden el encabezado `Authorization: Bearer <token>`. Cada organizador solo ve y cambia sus propios eventos y gestiones: los de otro responden 404.

| Método | Ruta | Qué hace | Sprint |
| --- | --- | --- | --- |
| GET | `/api/health/` | Comprueba que la API y la base de datos responden | 0 |
| POST | `/api/registro/` | Crea una cuenta y devuelve el token | 2 |
| POST | `/api/login/` | Inicia sesión y devuelve el token (dura 8 horas) | 2 |
| GET | `/api/organizador/me/` | Datos del organizador | 2 |
| GET, PUT | `/api/organizador/limite-diario/` | Ver o cambiar el límite diario de horas (6 por defecto, de 1 a 16) | 3 |
| GET, POST | `/api/eventos/` | Listar o crear eventos | 1 |
| GET, PUT, PATCH, DELETE | `/api/eventos/<id>/` | Ver, editar o eliminar un evento | 1 |
| GET | `/api/eventos/<id>/progreso/` | Total, hechas, pendientes y porcentaje del evento | 4 |
| GET, POST | `/api/eventos/<id>/subtareas/` | Listar o agregar gestiones de un evento | 1 |
| GET, PUT, PATCH, DELETE | `/api/subtareas/<id>/` | Ver, editar, reprogramar, marcar hecha, posponer o eliminar una gestión | 3–4 |
| GET | `/api/subtareas/hoy/` | Gestiones agrupadas en vencidas, para hoy y próximas (filtros `evento_id` y `estado`) | 2 |

Un evento guarda el contacto del cliente en tres campos: `cliente_nombre` (obligatorio), `cliente_telefono` y `cliente_correo` (al menos uno de los dos). `cliente_contacto` se sigue devolviendo, armado con esos tres.

Al editar o reprogramar una gestión, si el día queda por encima del límite diario la API no guarda y responde 409 con las cifras, fechas sugeridas y el primer día posterior donde sí cabe, para posponerla.

## Errores

Todas las respuestas son JSON, también los errores:

| Código | Cuándo | Cuerpo |
| --- | --- | --- |
| 400 | Datos inválidos | El campo con su mensaje, ej. `{"horas_estimadas": ["Las horas estimadas deben ser mayores a 0."]}` |
| 401 | Sin sesión o sesión vencida | `{"detail": "No autenticado. Debe iniciar sesión."}` |
| 404 | El recurso no existe, es de otro organizador o la ruta no existe | `{"detail": "..."}` |
| 409 | Sobrecarga del día al reprogramar | `{"detail": "Quedarías con 9h planificadas (límite 6h)", "codigo": "sobrecarga_diaria", "conflicto": {...}}` |
| 500 | Error inesperado (queda en los logs de Render) | `{"detail": "Algo salió mal de nuestro lado. Intenta de nuevo en un momento."}` |
