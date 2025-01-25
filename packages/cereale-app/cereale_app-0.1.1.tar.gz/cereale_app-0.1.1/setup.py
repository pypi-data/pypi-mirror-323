from setuptools import setup, find_packages

setup(
    name="cereale_app",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],
    author="krakiun",
    author_email="info@cereale.app",
    description="Python SDK for Cereale.app API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://bursadecereale.com/",
    project_urls={
        "Homepage": "https://bursadecereale.com/",
        "Developer": "https://krakiun.com/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)