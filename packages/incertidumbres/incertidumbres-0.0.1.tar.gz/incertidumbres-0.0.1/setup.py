from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Calcula incertidumbre de mediciones de laboratorio'
LONG_DESCRIPTION = 'Paquete creado con el proposito de realizar los calculos de incertidumbres de mediciones de laboratorio. Permite calcular error absoluto, desviación estandar, agregar calculos a hojas de datos'

# Configurando
setup(
       # el nombre debe coincidir con el nombre de la carpeta 	  
       #'modulomuysimple'
        name="incertidumbres", 
        version=VERSION,
        author="Emerson Warhman",
        author_email="<edwarhman@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["numpy", "sympy", "pandas", "openpyxl"], # añade cualquier paquete adicional que debe ser
        #instalado junto con tu paquete. Ej: 'caer'
        
        keywords=['python', 'incertidumbre', 'medicion indirecta'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
