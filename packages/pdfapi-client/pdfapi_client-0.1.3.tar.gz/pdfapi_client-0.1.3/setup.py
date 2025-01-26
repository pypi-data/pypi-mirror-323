from setuptools import setup, find_packages

setup(
    name="pdfapi-client",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
        "typing-extensions>=4.0.0",
        "certifi>=2021.10.8"
    ],
    author="pdfapi.dev",
    author_email="support@pdfapi.dev",
    description="Python client for pdfapi.dev - HTML to PDF conversion service",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pdfapi.dev",
    project_urls={
        "Documentation": "https://pdfapi.dev/",
        "Source": "https://github.com/pdfapi-dev-sdk/pdfapi-python-client",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Printing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="pdf conversion html api client",
    python_requires=">=3.7",
) 