from setuptools import setup, find_packages

setup(
    name="pookie",  # Unique name for your shell
    version="1.0.0",  # Version number
    description="A simple Python shell application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TeeWrath",
    author_email="subroto.2003@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[],  # List dependencies if applicable
    entry_points={
        'console_scripts': [
            'pookie=pookie.shell:main',  # command = package.module:function
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
