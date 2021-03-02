import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CFSIV_utils-Conradical",
    version="0.0.23",
    author="Conrad Storz IV",
    author_email="conradstorz@gmail.com",
    description="A collection of Time, Date, Filehandling and webscraping functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conradstorz/utilities.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
