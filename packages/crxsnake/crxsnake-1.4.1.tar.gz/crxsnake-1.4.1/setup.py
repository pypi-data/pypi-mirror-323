from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
requires = [
    "setuptools==75.8.0",
    "tortoise-orm==0.24.0",
    "disnake==2.10.1",
    "aiofiles==23.2.1",
    "loguru==0.7.2",
]
urls = {
    "Repository": "https://github.com/cyrax-dev/crxsnake",
    "Discord": "https://discord.gg/EEp67FWQDP",
}

setup(
    name="crxsnake",
    version="1.4.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CRX-DEV",
    author_email="cherniq66@gmail.com",
    url="https://discord.gg/EEp67FWQDP",
    license="MIT License",
    packages=find_packages(),
    install_requires=requires,
    project_urls=urls
)
