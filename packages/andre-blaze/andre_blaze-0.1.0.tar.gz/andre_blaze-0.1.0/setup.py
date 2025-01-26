from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="andre_blaze",
    version="0.1.0",
    author="Andre Ponce",
    author_email="admin@hopta.hn",
    description="Esta es la descripción del paquete",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://www.hopta.hn",

)
