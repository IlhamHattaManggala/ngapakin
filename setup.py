from setuptools import setup, find_packages

setup(
    name="ngapakin",
    version="1.0.6",
    description="Bahasa pemrograman berekstensi .ngpk dengan dialek Ngapak/Banyumasan & Larapak MVC Web Framework.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ilham Hatta Manggala",
    author_email="ilhamhattamanggala123@gmail.com",
    url="https://ilhamhattamanggala.my.id",
    project_urls={
        "Author Portfolio": "https://ilhamhattamanggala.my.id",
        "Source Code": "https://github.com/IlhamHattaManggala/ngapakin",
        "Bug Tracker": "https://github.com/IlhamHattaManggala/ngapakin/issues",
    },
    packages=find_packages(),
    py_modules=["ngapakin"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    extras_require={
        "mysql": ["pymysql>=1.0.0"],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "redis": ["redis>=4.5.0"],
        "security": ["argon2-cffi>=21.3.0"],
        "production": ["gunicorn>=20.1.0"],
        "all": ["pymysql>=1.0.0", "psycopg2-binary>=2.9.0", "redis>=4.5.0", "argon2-cffi>=21.3.0"],
    },
    entry_points={
        "console_scripts": [
            "ngapakin=ngapakin:main",
        ],
    },
)
