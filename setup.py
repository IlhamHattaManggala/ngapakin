from setuptools import setup, find_packages

setup(
    name="ngapakin",
    version="1.0.0",
    description="Bahasa pemrograman berekstensi .ngpk dengan dialek Ngapak/Banyumasan & Larapak MVC Web Framework.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ilham Hatta Manggala",
    author_email="ilham.hatta@example.com",
    url="https://github.com/IlhamHattaManggala/ngapakin",
    packages=find_packages(),
    py_modules=["ngapakin"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ngapakin=ngapakin:main",
        ],
    },
)
