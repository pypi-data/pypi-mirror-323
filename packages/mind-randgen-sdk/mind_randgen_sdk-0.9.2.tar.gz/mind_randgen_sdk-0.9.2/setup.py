from setuptools import setup, find_packages

setup(
    name="mind_randgen_sdk",
    version="0.9.2",
    author="Mind Network",
    author_email="dev@mindnetwork.xyz",
    description="Python SDK for Mind Network Randgen Hub FHE voting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mind-network/mind-sdk-randgen-py",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
