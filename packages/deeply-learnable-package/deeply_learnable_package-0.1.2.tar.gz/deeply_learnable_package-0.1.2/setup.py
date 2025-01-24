from setuptools import setup, find_packages

setup(
    name="deeply_learnable_package",  # Package name
    version="0.1.2",    # Initial version
    author="Konstantin",
    description="A package for regression, image processing, and classification",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "scikit-learn>=0.24.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
