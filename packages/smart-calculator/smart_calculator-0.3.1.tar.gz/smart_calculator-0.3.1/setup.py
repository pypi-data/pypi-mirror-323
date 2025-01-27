from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name="smart_calculator",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        # none for this version
    ],
    author="Chukwunonso Smart Agbawo",
    author_email= "chukwunonsosmartagbawo@gmail.com",
    maintainer="Chukwunonso Smart Agbawo",
    maintainer_email=  "chukwunonsosmartagbawo@gmail.com",
    entry_points={
        "console_scripts":[
            "smart_calculator = smart_calculator.__main__:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)