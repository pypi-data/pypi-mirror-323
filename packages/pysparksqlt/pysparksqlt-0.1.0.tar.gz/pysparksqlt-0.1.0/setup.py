from setuptools import setup, find_packages

setup(
    name="pysparksqlt",
    version="0.1.0",
    packages=find_packages(),
    description="PySpark SQL Tutorial Package",
    author="Your Name",
    install_requires=[
        "pyspark>=3.0.0",
    ],
    python_requires=">=3.6",
)