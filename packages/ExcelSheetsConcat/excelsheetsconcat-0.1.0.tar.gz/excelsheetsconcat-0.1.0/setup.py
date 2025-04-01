from setuptools import setup, find_packages

setup(
    name="ExcelSheetsConcat",  # Name of your package
    version="0.1.0",  # Version number
    author="Your Name",
    author_email="geniestat.andal@gmail.com",
    description="This package allow excel data handling",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/simeanhamado/exceldatahandler",  # Link to your repo
    packages=find_packages(),  # Automatically find packages
    install_requires=[  # List of dependencies
        "numpy",
        "pandas",
        "openpyxl",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python version requirement
)
