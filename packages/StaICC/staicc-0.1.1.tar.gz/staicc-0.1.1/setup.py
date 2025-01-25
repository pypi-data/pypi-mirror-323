import setuptools

with open("StaICC/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StaICC",
    version="0.1.1",
    author="Hakaze Cho",
    author_email="yfzhao@jaist.ac.jp",
    description="A standardized toolkit for classification task on In-context Learning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hc495/StaICC",
    packages=setuptools.find_packages(),
    package_data={"": ["*.dataset"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
    ],
)