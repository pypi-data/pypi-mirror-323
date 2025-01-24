from setuptools import setup, find_packages

setup(
    name="xltojson-converter",                         # Package name
    version="1.0.0",                         # Version
    description="A utility to convert Excel files to JSON",
    long_description_content_type="text/markdown",  # Markdown format
    author="Mahesh",
    author_email="maheshyamana123@gmail.com",
    url="https://github.com/yourusername/xltojson",  # Your project URL
    packages=find_packages(),               # Automatically find packages
    install_requires=[
        "openpyxl",                         # Dependency for working with Excel
    ],
    entry_points={
        "console_scripts": [
            "xltojson=xltojson.xltojson1:xltojson_cli",  # CLI entry point
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",                # Minimum Python version
)

