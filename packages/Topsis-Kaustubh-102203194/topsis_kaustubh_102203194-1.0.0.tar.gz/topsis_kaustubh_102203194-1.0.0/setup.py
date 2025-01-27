import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis_Kaustubh_102203194",
    version="1.0.0",
    description="Ranking alternatives based on similarity.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/4Kaustubh/Topsis-Kaustubh-102203194",
    author="Kaustubh Singh",
    author_email="91kaustubh@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "topsis=topsis.__main__:main",
        ]
    },
)
