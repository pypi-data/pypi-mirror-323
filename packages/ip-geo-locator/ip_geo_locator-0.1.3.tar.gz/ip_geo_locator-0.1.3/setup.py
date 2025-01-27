from setuptools import setup, find_packages

setup(
    name="ip_geo_locator",
    version="0.1.3",
    author="ip_geo_locator",
    author_email="your.email@example.com",
    description="A Python SDK for IP Finder",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/Three-mavericks/ip_finder_python.git",  # Update with your repo
    packages=["ip_geo_locator"],
    install_requires=[
        "requests>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)