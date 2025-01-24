from setuptools import setup, find_packages

setup(
    name="sqlalchemy-powerdrill",
    version="0.3.0",
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    install_requires=[
        "sqlalchemy>=1.4.0,<2.0.0",
        "requests>=2.31.0"
    ],
    entry_points={
        "sqlalchemy.dialects": [
            "powerdrill = powerdrill.base:PowerDrillDialect"
        ]
    },
    author="Powerdrill AI",
    author_email="support@powerdrill.ai",
    description="SQLAlchemy dialect for PowerDrill",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/powerdrill/powerdrill-sqlalchemy",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7"
)
