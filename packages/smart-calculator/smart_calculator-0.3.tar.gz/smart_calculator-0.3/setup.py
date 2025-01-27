from setuptools import setup, find_packages

setup(
    name="smart_calculator",
    version="0.3",
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
    }
)