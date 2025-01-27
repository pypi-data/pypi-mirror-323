import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="Topsis-Palak-102216032",  
    version="0.1.1",
    author="Palak Mahajan",
    author_email="",
    description="A Python package to perform TOPSIS analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/gitvivek14/Topsis-Vivek-102203778",  
    install_requires=[
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "topsis=topsis_palak.topsis:main",
        ],
    },
)
