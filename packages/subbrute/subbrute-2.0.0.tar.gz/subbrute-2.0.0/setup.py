from setuptools import setup, find_packages

setup(
    name="subbrute",
    version="2.0.0",
    description="A lightweight subdomain brute-forcing tool with live updates via callback.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MrFidal",
    author_email="mrfidal@proton.me",
    url="https://github.com/ByteBreach/subbrute",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
