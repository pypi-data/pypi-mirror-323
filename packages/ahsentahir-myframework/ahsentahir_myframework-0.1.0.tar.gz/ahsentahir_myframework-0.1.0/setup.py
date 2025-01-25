"""Setup configuration for MyFramework."""

from setuptools import setup, find_packages

setup(
    name="ahsentahir-myframework",
    version="0.1.0",
    author="Your Name",
    author_email="ahsentahir007@gmail.com",
    description="A Python framework for ML workflows(this one is for testing purpose only)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AhsenTahir/Py_Framework.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy==1.23.5",
        "pandas==1.5.3",
        "scikit-learn==1.2.2",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "pytest>=6.0.0",
        "black>=21.0",
        "isort>=5.0.0",
        "pytest-cov>=2.12.0",
    ],
) 