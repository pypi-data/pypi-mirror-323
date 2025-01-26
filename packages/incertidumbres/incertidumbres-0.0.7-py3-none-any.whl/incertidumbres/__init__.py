import sys
import os

from .incertidumbres import *

__all__ = [
    'calcular_incertidumbre',
    'calcular_medicion_indirecta',
    'evaluar_funcion',
    'eval_funcion_en_lista',
    'calcular_medicion_indirecta_en_lista',
    'separar_valores_incertidumbres',
    'separar_valores_incertidumbres_en_lista',
    'seleccionar_columnas_de_tabla',
    'agregar_calculo_a_dataframe',
]



def __incertidumbres_debug():
    # helper function so we don't import os globally
    import os
    debug_str = os.getenv('INCERTIDUMBRES_DEBUG', 'False')
    if debug_str in ('True', 'False'):
        return eval(debug_str)
    else:
        raise RuntimeError("unrecognized value for INCERTIDUMBRES_DEBUG: %s" %
                           debug_str)
INCERTIDUMBRES_DEBUG = __incertidumbres_debug()  # type: bool


del os
del sys