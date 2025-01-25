from setuptools import setup, find_packages

setup(
    name='agilent34400multimeter',  # Name deines Pakets
    version='0.1.4',            # Versionsnummer
    packages=find_packages(),   # Alle Pakete finden (in diesem Fall multimeter_control)
    install_requires=[          # Abhängigkeiten
        'pyvisa', 
        'visa',             # Die Bibliothek, die du für die Kommunikation mit dem Multimeter verwendest
    ],
    description='Python API for controlling Agilent 34400 series measurement devices',  # Kurze Beschreibung des Pakets
    long_description=open('README.md').read(),  # Längere Beschreibung aus der README-Datei
    long_description_content_type='text/markdown',  # Format der README-Datei
    author='Julian Steffens, Robin Binger',
    author_email='juliansf@mail.uni-paderborn.de',
    url='https://github.com/juliansteffens/agilent34400multimeter',  # GitHub-Repository-Link
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Python-Version, die unterstützt wird
)
