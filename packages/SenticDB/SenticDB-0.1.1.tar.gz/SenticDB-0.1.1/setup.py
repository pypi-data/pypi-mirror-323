from setuptools import setup, find_packages

setup(
    name="SenticDB",
    version="0.1.1",
    description="A lightweight SenticDB connector for Python 3.x",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sentic",
    author_email="senticsoftware@gmail.com",
    url="https://github.com/Sentic/SenticDB",
    packages=find_packages(),
    install_requires=[
        "pymongo>=4.0", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)