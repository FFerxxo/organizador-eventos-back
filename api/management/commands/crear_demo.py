"""
Crea (o deja como nueva) la cuenta demo para la evaluación del docente.

    python manage.py crear_demo

Las fechas se calculan desde hoy, así que al correrlo el día de la revisión
la cuenta trae gestiones vencidas, para hoy y próximas, hechas, pospuestas con
nota, un día lleno para probar el conflicto de sobrecarga y un evento al 100 %.
Si la cuenta ya existe, borra sus eventos y los vuelve a crear.
"""

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.estados import EN_CURSO, HECHA, POR_HACER, POSPUESTA
from api.models import Evento, Organizador, Subtarea

EMAIL_DEMO = "demo@eventflow.com"
PASSWORD_DEMO = "demo1234"
NOMBRE_DEMO = "Organizador Demo"
LIMITE_DEMO = Decimal("6")

# (días desde hoy, título, horas, estado, nota)
EVENTOS_DEMO = [
    {
        "nombre": "Boda de Laura y Andrés",
        "tipo": "Boda",
        "lugar": "Hacienda El Paraíso, Cali",
        "cliente_nombre": "Laura Gómez",
        "cliente_telefono": "300 555 1234",
        "cliente_correo": "",
        "dias_hasta_evento": 21,
        "gestiones": [
            (-5, "Reservar el salón", "2", HECHA, None),
            (-3, "Enviar invitaciones", "1.5", HECHA, None),
            (-2, "Confirmar el catering", "2", POR_HACER, None),
            (0, "Llamar al fotógrafo", "1", POR_HACER, None),
            (0, "Probar el menú con los novios", "3", EN_CURSO, None),
            (2, "Contratar la banda", "2", POSPUESTA,
             "Esperando la cotización de la segunda banda"),
            (4, "Decoración floral", "3", POR_HACER, None),
            (20, "Ensayo general", "2", POR_HACER, None),
        ],
    },
    {
        "nombre": "Lanzamiento Café Origen",
        "tipo": "Corporativo",
        "lugar": "Centro de Eventos Valle del Pacífico",
        "cliente_nombre": "Café Origen S.A.S.",
        "cliente_telefono": "",
        "cliente_correo": "eventos@cafeorigen.co",
        "dias_hasta_evento": 10,
        "gestiones": [
            (-1, "Imprimir volantes", "1", HECHA, None),
            # Mañana queda justo en el límite de 6 h: mover cualquier gestión
            # a ese día muestra el conflicto de sobrecarga.
            (1, "Buscar proveedor de sonido", "4", POR_HACER, None),
            (1, "Diseñar piezas gráficas", "2", POR_HACER, None),
            (3, "Confirmar lista de invitados", "1", POR_HACER, None),
        ],
    },
    {
        "nombre": "Cumpleaños de Sofía",
        "tipo": "Cumpleaños",
        "lugar": "Salón social Conjunto Los Robles",
        "cliente_nombre": "Marta Ruiz",
        "cliente_telefono": "315 222 3344",
        "cliente_correo": "marta.ruiz@correo.com",
        "dias_hasta_evento": 5,
        "gestiones": [
            (-4, "Comprar la torta", "1", HECHA, None),
            (-2, "Contratar recreacionista", "1.5", HECHA, None),
        ],
    },
]


def contacto(evento):
    """El texto único de contacto, armado como lo hace el serializer."""
    partes = (
        evento["cliente_nombre"],
        evento["cliente_telefono"],
        evento["cliente_correo"],
    )
    return " · ".join(parte for parte in partes if parte)


class Command(BaseCommand):
    help = "Crea o reinicia la cuenta demo con eventos de ejemplo para T1 a T4."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=EMAIL_DEMO)
        parser.add_argument("--password", default=PASSWORD_DEMO)

    @transaction.atomic
    def handle(self, *args, **opciones):
        email = opciones["email"].strip().lower()
        password = opciones["password"]
        hoy = timezone.localdate()

        organizador, creada = Organizador.objects.get_or_create(
            email=email,
            defaults={"nombre": NOMBRE_DEMO},
        )
        organizador.nombre = NOMBRE_DEMO
        organizador.password_hash = make_password(password)
        organizador.limite_horas_dia = LIMITE_DEMO
        organizador.save()

        # Se arranca de cero para que la demo siempre se vea igual.
        Evento.objects.filter(organizador=organizador).delete()

        total_gestiones = 0
        for datos in EVENTOS_DEMO:
            dia_evento = hoy + timedelta(days=datos["dias_hasta_evento"])
            evento = Evento.objects.create(
                organizador=organizador,
                nombre=datos["nombre"],
                tipo=datos["tipo"],
                lugar=datos["lugar"],
                cliente_nombre=datos["cliente_nombre"],
                cliente_telefono=datos["cliente_telefono"],
                cliente_correo=datos["cliente_correo"],
                cliente_contacto=contacto(datos),
                fecha_hora=timezone.make_aware(
                    datetime.combine(dia_evento, time(18, 0))
                ),
            )
            for dias, titulo, horas, estado, nota in datos["gestiones"]:
                Subtarea.objects.create(
                    evento=evento,
                    titulo=titulo,
                    fecha_objetivo=hoy + timedelta(days=dias),
                    horas_estimadas=Decimal(horas),
                    estado=estado,
                    nota=nota,
                )
                total_gestiones += 1

        accion = "creada" if creada else "reiniciada"
        self.stdout.write(self.style.SUCCESS(
            f"Cuenta demo {accion}: {email} / {password} "
            f"({len(EVENTOS_DEMO)} eventos, {total_gestiones} gestiones)."
        ))
