from setuptools import setup, find_packages

setup(
    name="QwantAI",
    version="1.0.0",
    description="A Python library to interact with the Qwant search engine.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ramona",
    url="https://github.com/Ramona-Flower/QwantAI",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests==2.31.0",
        "websocket-client==1.6.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
