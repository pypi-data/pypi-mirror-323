from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="flatpack",
    version="3.12.129",
    license="Apache-2.0",
    packages=find_packages(),
    package_data={
        'flatpack': ['resources/python_executor.py'],
    },
    include_package_data=True,
    python_requires=">=3.10.0, <3.13.0",
    install_requires=[
        "aiofiles==24.1.0",
        "beautifulsoup4==4.12.3",
        "croniter==6.0.0",
        "cryptography==44.0.0",
        "fastapi==0.115.6",
        "hnswlib==0.8.0",
        "httpx==0.28.1",
        "itsdangerous==2.2.0",
        "ngrok==1.4.0",
        "psutil==6.1.1",
        "pydantic==2.10.5",
        "pypdf==5.1.0",
        "python-multipart==0.0.20",
        "requests==2.32.3",
        "rich==13.9.4",
        "sentence-transformers==3.3.1",
        "toml==0.10.2",
        "uvicorn==0.34.0",
        "zstandard==0.23.0"
    ],
    author="Flatpack",
    author_email="dev@ƒlatpack.ai",
    description="Ready-to-assemble AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RomlinGroup/Flatpack",
    entry_points={
        "console_scripts": [
            "flatpack=flatpack.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only"
    ]
)
