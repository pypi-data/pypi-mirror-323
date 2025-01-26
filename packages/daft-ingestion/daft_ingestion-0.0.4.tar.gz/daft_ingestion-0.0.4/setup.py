from setuptools import setup, find_packages

# Lê o requirements.txt
def parse_requirements(filename):
    with open(filename, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="daft_ingestion",
    version="0.0.4",
    author="Douglas B. Martins",
    author_email="douglas@meizter.com",
    description="lakehouse with daft",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,  # Inclui os arquivos especificados no MANIFEST.in
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
