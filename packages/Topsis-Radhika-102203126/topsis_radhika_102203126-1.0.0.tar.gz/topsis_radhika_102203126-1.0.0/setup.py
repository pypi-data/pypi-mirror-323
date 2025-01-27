from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Topsis-Radhika-102203126",
    version="1.0.0",
    description="A brief description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Radhika Rajdev",
    url="https://github.com/radhikarajdev/topsis_ds.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],  # Add dependencies here
)
