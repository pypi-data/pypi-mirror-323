from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis_AnirudhGarg_102203573",
    version="1.0.14",
    author="Anirudh Garg",
    author_email="agarg3_be22@thapar.com",
    url="https://github.com/agarg2004/Topsis-Assignment",
    description="A python package for implementing topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "numpy"],
    entry_points={"console_scripts": ["Topsis_AnirudhGarg_102203573 = Topsis_AnirudhGarg_102203573.topsis:main"]},
)