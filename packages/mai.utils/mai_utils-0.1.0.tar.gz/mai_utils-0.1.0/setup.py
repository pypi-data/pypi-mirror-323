from setuptools import setup, find_packages

setup(
    name="mai.utils",
    version="0.1.0",
    description="Shared utility functions for the MAI project.",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        # Add dependencies here, e.g. "numpy>=1.21.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
