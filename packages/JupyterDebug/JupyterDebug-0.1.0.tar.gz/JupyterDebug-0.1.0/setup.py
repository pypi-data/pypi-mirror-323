from setuptools import setup, find_packages

setup(
    name="JupyterDebug",
    version="0.1.0",
    author="Ethan",
    author_email="your.email@example.com",
    description="A package for debugging Jupyter notebooks using OpenAI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/et22/JupyterDebug",
    packages=find_packages(),
    install_requires=[
        "openai>=1.9.0",
        "ipython>=7.34.0",
        "ipywidgets>=7.7.1",
    ],
    extras_require={
        "test": ["pytest>=6.0.0"],
        "dev": ["black>=22.0.0", "flake8>=4.0.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)