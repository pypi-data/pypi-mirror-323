from setuptools import setup

setup(
    name="102217211_Ashmeet_topsis",
    version="1.1.0",
    author="Ashmeet Kaur",
    author_email="akaur9_be22@thapar.edu",
    description="A Python package for TOPSIS calculation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ashmkaur/102217211_Ashmeet_topsis",
    packages=["102217211_Ashmeet_topsis"],
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
            "102217211_Ashmeet_topsis=102217211_Ashmeet_topsis.topsis:main",
        ],
    },
)
