from setuptools import setup, find_packages

setup(
    name="appsniffer",  # Название пакета
    version="1.0.0",  # Версия
    author="Avinion",  # Ваше имя
    author_email="shizofrin@gmail.com",  # Ваш email
    url="https://t.me/+VFiT6gd42ehhNzYy",  # Сайт проекта
    description="Интерактивный скрипт для поиска информации о приложениях в Google Play Market.",
    long_description=open("README.md", "r", encoding="utf-8").read(),  # Описание из README.md
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Автоматически находит пакеты
    install_requires=[
        "google-play-scraper",  # Зависимости
    ],
    entry_points={
        "console_scripts": [
            "appsniffer=appsniffer.main:main",  # Команда для запуска скрипта
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Минимальная версия Python
)