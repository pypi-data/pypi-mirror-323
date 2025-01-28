from setuptools import setup, find_packages

setup(
    name="lavaru_capital",
    version="0.1.2",
    author="megavaru",
    author_email="anon@anon.anon",
    description="De la megavaru pentru veri",
    package_dir={"": "src"},  
    packages=find_packages(where="src"),  
    install_requires=[
        "pandas_ta",
        "pandas",
        "ccxt",
        "numpy",
        "plotly",
    ],
    python_requires=">=3.11", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
)


