from setuptools import setup, find_packages

setup(
    name="ThreadedSQLite",
    version="0.1.0",
    description="Simplifying SQLite access.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="David Lorenzana",
    author_email="davlorenzana@gmail.com",
    url="https://github.com/tu_usuario/mi_modulo",
    packages=find_packages(),
    install_requires=[
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)
