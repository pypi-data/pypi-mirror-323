from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zohlathu",
    version="2.0.8",
    author="RSR",
    author_email="imrsrmizo@gmail.com",
    description="A A Python package for fetching Mizo song lyrics from Zohlathu.in",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RSR-TG-Info/ZoHlathu",
    packages=find_packages(),
    install_requires=[
        "requests",
        "feedparser",
        "html2text",
        "youtube_search",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
