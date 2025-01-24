from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aitronos-logger",
    version="0.1.0",
    author="Phillip Loacker",
    author_email="phillip@aitronos.com",
    description="A sophisticated JSON-based logging system with insights and time estimation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philliploacker/aitronos-python-logger",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.8",
    install_requires=[],
) 