from setuptools import setup, find_packages

setup(
    name="pystorm10xmypackage",                     # Название пакета
    version="1.0.0",                      # Версия пакета
    description="Пример Python-пакета",   # Краткое описание
    long_description=open("README.md").read(),  # Полное описание
    long_description_content_type="text/markdown",
    author="PyStorm10x",                    # Автор
    author_email="staholos@mail.ru", # Email автора
    url="https://github.com/PyStorm10x/mypackage",  # URL репозитория
    license="MIT",                        # Лицензия
    packages=find_packages(),             # Поиск модулей
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",              # Минимальная версия Python
)
