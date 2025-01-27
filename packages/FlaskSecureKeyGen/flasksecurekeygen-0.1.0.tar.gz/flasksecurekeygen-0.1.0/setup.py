from setuptools import setup, find_packages

setup(
    name="FlaskSecureKeyGen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Ch. Abdul Wahab",
    author_email="ch.abdul.wahab310@gmail.com",
    description="A library to generate secure random secret keys for Flask apps.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ChAbdulWahhab/FlaskSecureKeyGen",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)