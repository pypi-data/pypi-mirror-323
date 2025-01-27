from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyutils-sqlmodel",
    version="0.2.3",
    description="Configuracion inicial hacia conexion a base de datos con SQLModel y un repositorio con las operaciones CRUD utilizando genericos para el ahorro de codigo",
    author="Christian Carballo Cano",
    author_url="https://www.linkedin.com/in/cano2908/",
    maintainer="Christian Carballo Cano",
    maintainer_email="c.cano2908@outlook.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "python-dotenv==1.0.1",
        "psycopg2-binary==2.9.10",
        "setuptools==75.6.0",
        "sqlmodel==0.0.22",
    ],
)
