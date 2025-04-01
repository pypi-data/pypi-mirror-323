from setuptools import setup, find_packages

setup(
    name="cognixis",  # Package name
    version="0.1.9",  # Initial version
    description="A PyTorch training loop utility",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sidh2690",
    author_email="sidhu2690@gmail.com",
    url="https://github.com/sidhu2690/CogniXis",  # Your GitHub repository URL
    packages=find_packages(),
    install_requires=[
        "torch>=1.0",  # PyTorch 
        "torchinfo>=1.7",
        "numpy"  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
