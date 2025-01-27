from setuptools import setup, find_packages

setup(
    name="Topsis-Gurshan-102203008",  # The name of the package
    version="0.1.0",  # Initial version
    author="Gurshan Singh Cheema",  # Your name
    author_email="gurshan94u@gmail.com",  # Your email
    description="A Python package implementing the TOPSIS method",  # Short description of the package
    long_description=open('README.md').read(),  # Read the README for long description
    long_description_content_type="text/markdown",  # Format of the long description
    url="https://github.com/gurshan94/Topsis-Gurshan-102203008",  # GitHub URL or your project URL
    packages=find_packages(),  # Automatically discover and include your package
    classifiers=[  # Classifiers to help people find your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify the required Python version
    install_requires=[],  # List any external dependencies here
)
