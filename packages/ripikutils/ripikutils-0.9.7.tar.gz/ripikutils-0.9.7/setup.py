from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ripikutils",
    version="0.9.7",
    author="Vaibhav Agarwal",
    author_email="vaibhav@ripik.ai",
    description="A utility package for AWS S3 and MongoDB operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ripiktech/ripikutils",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ],
    license="MIT",  # Added this line
    python_requires=">=3.10",
    install_requires=[
        "boto3",
        "pymongo",
        "certifi",
        "numpy==1.26.3",
        "typesentry==0.2.7"
    ],
)
