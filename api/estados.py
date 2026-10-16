
"""
Estados de una gestión. Se mantienen equivalencias para compatibilidad
con valores utilizados anteriormente.
"""

POR_HACER = "por hacer"
EN_CURSO = "en curso"
HECHA = "hecha"
POSPUESTA = "pospuesta"

ESTADOS = [POR_HACER, EN_CURSO, HECHA, POSPUESTA]

EQUIVALENTES = {
    "pendiente": POR_HACER,
    "en_progreso": EN_CURSO,
    "en progreso": EN_CURSO,
    "finalizado": HECHA,
}

MENSAJE_ESTADO_INVALIDO = (
    "Estado inválido. Usa: por hacer, en curso, hecha o pospuesta."
)


def normalizar_estado(valor):
    """Devuelve el estado normalizado, o None si no es válido."""
    estado = str(valor or "").strip().lower()
    estado = EQUIVALENTES.get(estado, estado)
    return estado if estado in ESTADOS else None


def formas_de(estado):
    """Todas las formas en que un estado puede estar guardado en la base."""
    return [
        estado,
        *[vieja for vieja, nueva in EQUIVALENTES.items() if nueva == estado],
    ]
