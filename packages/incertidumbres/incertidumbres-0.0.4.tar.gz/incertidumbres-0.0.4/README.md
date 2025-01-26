# Incertidumbres

Paquete creado con el proposito de realizar los calculos de incertidumbres de mediciones de laboratorio. Permite calcular error absoluto, desviación estandar, agregar calculos a hojas de datos

## Instalación

Para instalar el paquete, puedes usar pip:

```
pip install incertidumbres
```

## Uso

Para usar el paquete, puedes importarlo en tu código Python:

```python
from incertidumbres import calcular_incertidumbre

# Ejemplo de uso
datos = [1, 2, 3, 4, 5]
incertidumbre = calcular_incertidumbre(datos)
print(incertidumbre)
```

Este código imprimirá el valor de la incertidumbre para los datos proporcionados.
