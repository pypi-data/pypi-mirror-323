from sympy import symbols
from incertidumbres import evaluar_funcion, calc_error_absoluto, calc_desviacion_estandar

vo, vi = symbols('vo vi')
f = vo/vi

variables = [vo, vi]
valores = [0.48, 0.52]
incertidumbres = [0.04, 0.04]

result = evaluar_funcion(f, variables, valores)
print(result)

errorAbsoluto = calc_error_absoluto(f, variables, valores, incertidumbres)
print(errorAbsoluto)

desviacionEstandar = calc_desviacion_estandar(f, variables, valores, incertidumbres)
print(desviacionEstandar)
