from setuptools import setup, find_packages
import pathlib

current_dir = pathlib.Path(__file__).parent
long_description = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="matebotpy", 
    version="1.0.1",
    description="Python API Wrapper for Matebot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Máté Mészáros",
    author_email="meszmatew@gmail.com",
    url="https://github.com/meszmate/matebotpy",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
)