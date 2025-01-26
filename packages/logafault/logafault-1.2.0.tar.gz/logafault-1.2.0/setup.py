from setuptools import find_packages, setup

# Read the README file for long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="logafault",
    version="1.2.0",
    description="An SDK for interacting with CityPower's APIs.",
    packages=find_packages(),  # Automatically finds all packages
    include_package_data=True,
    package_data={"logafault": ["py.typed"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cliftondhanee/logafault",
    author="Clifton Dhanee",
    author_email="clifton.dhanee@yahoo.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "pydantic"],
    python_requires=">=3.9",
)
