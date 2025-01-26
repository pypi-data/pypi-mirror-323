from setuptools import setup, find_packages

setup(
    name="Topsis-Harshil-102217020",
    version="1.0.0",
    author="Harshil Garg",
    author_email="your_email@example.com",  # Replace with your email
    description="A Python package to implement the TOPSIS algorithm for decision-making.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Harshil7051/Topsis-Harshil-102217020",
    packages=find_packages(),
    install_requires=["pandas", "numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
