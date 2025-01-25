from setuptools import setup, find_packages

setup(
    name="disk_cached",
    version="0.1.0",
    description="A simple module for caching with diskcache.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="David Lorenzana",
    author_email="tu_email@example.com",
    url="https://github.com/tu_usuario/mi_modulo",
    packages=find_packages(),
    install_requires=[
        "diskcache>=5.6.1",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)
