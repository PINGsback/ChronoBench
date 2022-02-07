from setuptools import setup, find_packages

requirements = ["psutil>=5"]

setup(
    name="chronobench",
    version="0.0.1",
    author="yo mum",
    author_email="pingsback@gmail.com",
    description="A really bad benchmark test for chrome os.",
    url="https://github.com/PINGsback/ChronoBench/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)