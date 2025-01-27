from setuptools import setup, find_packages

setup(
    name="Topsis-Aryan-102213016",
    version="1.0.0",
    author="Aryan Bakshi",
    author_email="bakshiaryan01@gmail.com",
    description="A Python package for TOPSIS-based decision-making.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aryanbakshi04/Topsis_Aryan_Bakshi_102213016",  
    packages=find_packages(),
    install_requires=["pandas", "numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:main",
        ],
    },
)
