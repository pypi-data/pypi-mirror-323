from setuptools import setup

readme = open("README.md", "r")
README_TEXT = readme.read()
readme.close()

setup(
    name="the-running-api",
    version="0.3.1",
    description="A library for analyzing data from distance runners",
    long_description_content_type="text/markdown",
    long_description=README_TEXT,
    author="csacco",
    url="https://github.com/csacco1/running-api",
    install_requires=[
        "fitparse",
        "gpxpy",
        "pandas",
        "plotly",
        "pydantic",
        "marshmallow",
        "numpy",
        "jupyter",
        "scikit-learn",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    py_modules=[],
)
