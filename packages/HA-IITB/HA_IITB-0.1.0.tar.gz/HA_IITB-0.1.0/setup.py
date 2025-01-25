from setuptools import setup, find_packages

setup(
    name="HA_IITB",  
    version="0.1.0", 
    author="dhinwaji",
    author_email="ddhinwa05@gmail.com",
    description="HA IIT Bombay",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Deepak-Dhinwa/HA_IITB.git",  # GitHub repository or project URL
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Specifies the MIT license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
