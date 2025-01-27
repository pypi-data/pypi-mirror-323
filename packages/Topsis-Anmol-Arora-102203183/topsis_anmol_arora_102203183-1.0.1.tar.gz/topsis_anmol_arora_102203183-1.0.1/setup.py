from setuptools import setup, find_packages

setup(
    name="Topsis-Anmol-Arora-102203183",  # Replace with your package name
    version="1.0.1",  # Increment the version
    author="Anmol-Arora",
    author_email="aarora_be22@thapar.edu",
    description="A Python package for performing TOPSIS analysis.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Anmol-Arora2309/Predictive-Analysis-Topsis",  # Replace with your GitHub URL
    packages=find_packages(),
    install_requires=["pandas", "numpy", "openpyxl"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
