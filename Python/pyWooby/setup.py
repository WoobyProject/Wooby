import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyWooby", # Replace with your own username
    version="0.0.1",
    author="Enrique Maldonado",
    author_email="contact@iamemgineer.com",
    description="A Python package for the dev of Wooby",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WoobyProject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)