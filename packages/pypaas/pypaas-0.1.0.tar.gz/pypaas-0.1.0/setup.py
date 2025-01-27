from setuptools import setup, find_packages

setup(
    name="pypaas",
    version="0.1.0",
    description="Python as a Service (pypaas): A library for creating Python-based tasks without worrying about deployment.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Michael Ben Yosef",
    author_email="mishico5@gmail.com",
    url="https://github.com/BarBQ-code/pypaas",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
