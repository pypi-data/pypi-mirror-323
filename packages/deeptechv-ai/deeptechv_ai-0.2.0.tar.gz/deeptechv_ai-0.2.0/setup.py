from setuptools import setup, find_packages

setup(
    name="deeptechv_ai",
    version="0.2.0",
    author="Techvantage",
    description="Techvantage AI Developer Toolkit for Deepseek",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["openai", "requests"],
    entry_points={
        "console_scripts": [
            "deeptechv_ai=deeptechv_ai.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)