from setuptools import setup

setup(
    name="topsis_calculator_abhai",
    version="2.1.0",
    author="abahji",
    author_email="your_email@example.com",
    description="A Python package for TOPSIS calculation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/topsis-calculator",
    packages=["topsis_calculator_abhai"],
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
            "topsis_calculator_abhai=topsis_calculator_abhai.topsis:main",
        ],
    },
)
