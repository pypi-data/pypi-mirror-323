
from setuptools import setup, find_packages
setup(
    name='pixegamii_hello',
    version='0.2',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pixegami-hello = pixegami_hello:hello",
        ],
    },   
)