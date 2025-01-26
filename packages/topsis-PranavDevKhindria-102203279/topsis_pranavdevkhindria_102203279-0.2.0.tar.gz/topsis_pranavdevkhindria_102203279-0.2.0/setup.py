from setuptools import setup, find_packages

setup(
    name="topsis-PranavDevKhindria-102203279",            # Package name on PyPI
    version="0.2.0",                             # Package version
    author="Pranav",
    description="A Python package to perform Topsis analysis.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/oxzoid/Topsis-package",
    packages=find_packages(),                    # Automatically find subpackages
    include_package_data=True,                   # If you have data files, etc.
    install_requires=[
        "pandas",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "topsis-calc=topsis_PranavDevKhindria_102203279.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)
