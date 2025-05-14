from setuptools import setup, find_packages
from pathlib import Path

# read the long description from README.md
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

setup(
    name="binom_misprice",
    version="0.1.0",
    author="Shanmukha Sai Katlaparthi",
    author_email="skatlapa@stevens.edu",
    description="Vectorized binomial-tree option mispricing with parallel processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shanmukha96/binom-misprice",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "yfinance",
    ],
    extras_require={
        "dev": [
            "pytest",
            "requests-cache", 
            "setuptools"
        ]
    },
    entry_points={
        "console_scripts": [
            "binom-misprice=binom_misprice.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
