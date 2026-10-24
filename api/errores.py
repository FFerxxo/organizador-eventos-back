"""
Respuestas de error en JSON para toda la API.

El front siempre espera un JSON con `detail` (o los campos con su error).
Sin esto, un fallo inesperado o una ruta que no existe devuelven la página
HTML de Django y el front no puede mostrar un mensaje claro.
"""

import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("api")

MENSAJE_ERROR_SERVIDOR = (
    "Algo salió mal de nuestro lado. Intenta de nuevo en un momento."
)
MENSAJE_RUTA_NO_EXISTE = "La ruta que buscas no existe."


def manejar_excepcion(exc, context):
    """
    Deja que DRF responda los errores que conoce (400, 401, 404, 405...).
    Cualquier otro error queda registrado en el log y se responde 500 en JSON.
    """
    respuesta = exception_handler(exc, context)
    if respuesta is not None:
        return respuesta

    vista = context.get("view")
    logger.exception(
        "Error inesperado en %s",
        vista.__class__.__name__ if vista else "la API",
        exc_info=exc,
    )
    return Response(
        {"detail": MENSAJE_ERROR_SERVIDOR},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def ruta_no_encontrada(request, exception=None):
    return JsonResponse({"detail": MENSAJE_RUTA_NO_EXISTE}, status=404)


def error_del_servidor(request):
    return JsonResponse({"detail": MENSAJE_ERROR_SERVIDOR}, status=500)
