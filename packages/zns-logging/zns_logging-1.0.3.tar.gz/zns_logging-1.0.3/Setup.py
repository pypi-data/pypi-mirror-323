from setuptools import setup, find_packages

setup(
    name="zns_logging",
    version="1.0.3",
    description="A simple and flexible logging library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Zennisch",
    author_email="zennisch@gmail.com",
    url="https://github.com/Zennisch/pypi_zns_logging",
    packages=find_packages(),
    install_requires=[
        "colorama"
    ],
    python_requires=">=3.10",
)
