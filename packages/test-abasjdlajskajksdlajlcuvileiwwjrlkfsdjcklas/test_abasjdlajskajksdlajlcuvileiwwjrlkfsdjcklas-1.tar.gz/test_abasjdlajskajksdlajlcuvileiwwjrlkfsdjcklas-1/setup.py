from setuptools import setup, find_packages

setup(
    name="test---abasjdlajskajksdlajlcuvileiwwjrlkfsdjcklas",
    version="1",
    author="Stefan Resch",
    author_email="stefan.resch@oeaw.ac.at",
    description="test---abasjdlajskajksdlajlcuvileiwwjrlkfsdjcklas",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://example.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["PyYAML>=6.0.2"],
    packages=["test"],
    package_dir={"test": "."},
    # include_package_data=True,
    # package_data={"": ["README.md"]},
)
