from setuptools import setup, find_packages

setup(
    name="GhostGate",  # Nom du package
    version="1.0.0",  # Version initiale
    author="Ton Nom",
    author_email="ton.email@example.com",
    description="Une librairie Python pour diverses tâches système.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ton-repo/ghostgate",  # Mets un lien vers ton repo GitHub
    packages=find_packages(),
    install_requires=[
        "requests",
        "pycryptodome",
        "aiohttp",
        "psutil",
        "httpx",
        "pillow",
        "simplejson",
        "pywin32",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
