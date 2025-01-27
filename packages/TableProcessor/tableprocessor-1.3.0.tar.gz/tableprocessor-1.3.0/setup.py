from setuptools import setup, find_packages

setup(
    name="TableProcessor",
    version="1.3.0",
    description="Procesamiento de tablas de datos",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "tqdm",
        "openpyxl",
        "xlsxwriter",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)