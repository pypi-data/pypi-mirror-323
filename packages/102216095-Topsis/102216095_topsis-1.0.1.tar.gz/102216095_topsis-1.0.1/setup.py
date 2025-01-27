from setuptools import setup, find_packages

setup(
    name="102216095_Topsis", 
    version="1.0.1",
    author="Sayak Mukherjee",
    author_email="your.email@example.com",
    description="A Python implementation of the TOPSIS decision-making method",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:main",  # Expose the CLI command
        ],
    },
    python_requires=">=3.6",
)
