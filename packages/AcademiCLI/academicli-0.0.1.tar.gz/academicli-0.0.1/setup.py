from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="AcademiCLI",
    version="0.0.1",
    author="Seyed Hossein Ahmadpanah",
    author_email="djalicrt@gmail.com",
    description="CLI tool to fetch Google Scholar metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmadpanah/AcademiCLI",
    packages=find_packages(),
    install_requires=[
        'scholarly',
        'requests',
        'beautifulsoup4'
    ],
    entry_points={
        'console_scripts': [
            'AcademiCLI=AcademiCLI.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)