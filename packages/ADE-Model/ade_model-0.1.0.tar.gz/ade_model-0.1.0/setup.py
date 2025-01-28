from setuptools import setup, find_packages

setup(
    name="ADE_Model",  # Unique package name
    version="0.1.0",  # Initial version
    description="ADE Detection Model for Adverse Drug Events",
    long_description=open("README.md").read(),  # Use your README for the PyPI page
    long_description_content_type="text/markdown",  # Specify markdown format
    author="Heet Bhuva",  # Your name
    author_email="heetbhuva18@gmail.com",  # Your email
    url="https://github.com/heetbhuva1801/ADE_Model.git",  # GitHub repo URL
    packages=find_packages(),  # Automatically find packages in the project
    include_package_data=True,  # Include non-code files like model files
    install_requires=[
        "tensorflow>=2.0",
        "transformers>=4.0",
    ],
    python_requires=">=3.6",  # Specify the minimum Python version
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
