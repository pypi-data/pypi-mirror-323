import setuptools
from pathlib import Path

#path de la descripcion
long_desc = Path('readme.md').read_text()

setuptools.setup(
    name="holamundoprueba2025pypih",
    version="0.0.1",
    long_description=long_desc,
    packages= setuptools.find_packages(
        exclude=['mocks','tests']
    )
)