# setup.py
from setuptools import setup, find_packages

setup(
    name="fastboot",
    version="0.1.0",
    description="A lightweight FastAPI framework inspired by Spring Boot, focusing on modularization and automation.",
    author="qintianming",
    author_email="qintianming511@gmail.com",
    url="",  # 没有可以先空着
    packages=find_packages(exclude=["tests*", "config*", "controllers*", "services*", "repositories*", "models*"]),
    include_package_data=True,
    install_requires=[
        "annotated-types>=0.7.0",
        "anyio>=4.9.0",
        "certifi>=2025.4.26",
        "charset-normalizer>=3.4.1",
        "click>=8.1.8",
        "colorama>=0.4.6",
        "fastapi>=0.115.12",
        "h11>=0.16.0",
        "httpcore>=1.0.9",
        "httpx>=0.28.1",
        "idna>=3.10",
        "mysqlclient>=2.2.7",
        "peewee>=3.17.9",
        "pydantic>=2.11.3",
        "pydantic_core>=2.33.1",
        "PyYAML>=6.0.2",
        "requests>=2.32.3",
        "sniffio>=1.3.1",
        "starlette>=0.46.2",
        "typing-inspection>=0.4.0",
        "typing_extensions>=4.13.2",
        "urllib3>=2.4.0",
        "uvicorn>=0.34.2"
    ],
    python_requires=">=3.8",  # 根据依赖包的要求提高了Python版本要求
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
