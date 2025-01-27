from setuptools import setup, find_packages

setup(
    name="Topsis_Armandeep_Singh_Dhillon_102216076", 
    version="1.0.0",
    author="Armandeep_Singh_Dhillon",
    author_email="your.email@example.com",
    description="A Python implementation of the TOPSIS decision-making method",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dhillonarman/Topsis-Armandeep-102216076",  
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
