from setuptools import setup, find_packages

setup(
    name="Body_size",
    version="0.2.1",
    author="Tran Ngoc Huy",
    author_email="ngochuy2742@gmail.com",
    description="A package to calculate body size about [uk_size, usa_size, uk_chart]",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Huy132446/body-size",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)