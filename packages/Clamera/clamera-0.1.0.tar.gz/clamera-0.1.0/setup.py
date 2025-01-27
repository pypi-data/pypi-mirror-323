from setuptools import setup, find_packages

setup(
    name="Clamera",
    version="0.1.0",   
    description="A versatile 2D camera library for top-down games using Pygame.",
    author="Clart",
    author_email="lmk.kadlecek@gmail.com",
    url="https://github.com/ClartTheRoyalAcademyOfArt/Clamera",
    packages=find_packages(),
    install_requires=[
        "pygame"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)