from pathlib import Path # > 3.6
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Información del paquete
VERSION = '0.1.4'
DESCRIPTION = 'Permite enviar correos electrónicos con plantillas DOCX.'
PACKAGE_NAME = 'sendmail-docx'
AUTHOR = 'José María Sánchez González'
EMAIL = 'jmsanchez.ibiza@gmail.com'
GITHUB_URL = 'https://github.com/jmsanchez-ibiza/sendmail-docx'
# --------------------------------------------


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    author=AUTHOR,  
    author_email=EMAIL,
    url=GITHUB_URL,
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'python-docx',
        'python-dotenv',
        'mammoth',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
