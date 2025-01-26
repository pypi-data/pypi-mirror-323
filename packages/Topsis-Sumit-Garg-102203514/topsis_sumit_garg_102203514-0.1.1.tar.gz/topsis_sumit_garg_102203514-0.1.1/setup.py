from setuptools import setup

setup(
    name="Topsis_Sumit_Garg_102203514",
    version="0.1.1",
    author="Sumit Garg",
    author_email="sumit0000garg@gmail.com",
    description="A Python package for TOPSIS calculation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/topsis-calculator",
    packages=["Topsis_Sumit_Garg_102203514"],
    install_requires=[
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "Topsis_Sumit_Garg_102203514= Topsis_Sumit_Garg_102203514.topsis:main",
        ],
    },
)
