from setuptools import setup, find_packages

setup(
    name='dualcode',  # Nombre de tu paquete
    version='1.0.0',             # Versión de tu paquete
    packages=find_packages(),  # Buscar todos los paquetes en el directorio
    install_requires=[],       # Si tu paquete depende de otros paquetes, ponlos aquí
    description='A package to manage variables in a JSON file',  # Descripción corta
    long_description=open('README.md').read(),  # Descripción larga del paquete (es recomendable incluirla)
    long_description_content_type='text/markdown',  # Especificar que es Markdown
    author='Maximiliano David Sanchez',        # Tu nombre
    author_email='maximilianosanchez1304@gmail.com',  # Tu correo
    license='IST',             # Licencia que estás usando
    classifiers=[  # Clasificación del paquete
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
