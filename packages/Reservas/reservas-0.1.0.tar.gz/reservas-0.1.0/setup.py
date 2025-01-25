from setuptools import setup, find_packages

setup(
    name="Reservas",  
    version="0.1.0",   
    author="Navil Lugo Taveras",
    author_email="nafa8@hotmail.com",
    description="Descripción breve de tu paquete",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Encuentra automáticamente los paquetes en tu proyecto
    package_data={
        'src': ['config.json'],  # Asegúrate de que 'src' es el nombre de tu paquete
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Especifica la versión mínima de Python

    # Configuración para py2exe
    options={
        'py2exe': {
            'bundle_files': 1,  # Combina todo en un solo archivo ejecutable
            'compressed': True,  # Comprime los archivos para reducir el tamaño
            'includes': ['ui.Menu', 'src.Menu_logic'],  # Incluye módulos necesarios
        }
    },
    zipfile=None,  # Evita que se genere un archivo zip separado
    console=[{
        'script': 'src/Appmain.py' # Archivo principal de tu aplicación
        
    }],
)