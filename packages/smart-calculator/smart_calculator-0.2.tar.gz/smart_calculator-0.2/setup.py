from setuptools import setup, find_packages

setup(
    name="smart_calculator",
    version="0.2",
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
            "addition = smart_calculator:addition",
            "subtraction = smart_calculator:sub",
            "multiplication = smart_calculator:mult",
        ],
    }
)