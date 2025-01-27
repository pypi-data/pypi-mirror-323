from setuptools import setup, find_packages

setup(
    name="Topsis-Mandar-102203163",
    version="1.0",       
    author="Mandar",
    author_email="mandargarud1811@gmail.com",
    description="A Python Package which creates topsis rankings on the basis of performance scores",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/mandarmgd/topsis", 
    install_requires=[
        "numpy",
        "pandas",
        "scipy", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:main",
        ],
    },
)