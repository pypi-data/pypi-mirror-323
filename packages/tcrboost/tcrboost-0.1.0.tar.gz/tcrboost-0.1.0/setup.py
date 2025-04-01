from setuptools import setup, find_packages

setup(
    name="tcrboost",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
    ],
    author="Zhiao Shi",
    author_email="zhiao.shi@gmail.com",
    description="T-Cell Receptor Bayesian Optimization of Specificity and Tuning",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zhiaos/tcrboost",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 