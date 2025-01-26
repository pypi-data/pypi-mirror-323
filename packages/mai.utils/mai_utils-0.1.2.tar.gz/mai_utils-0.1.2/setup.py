from setuptools import setup, find_packages

setup(
    name="mai.utils",
    version="0.1.2",
    description="Shared utility functions for the MAI project.",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
