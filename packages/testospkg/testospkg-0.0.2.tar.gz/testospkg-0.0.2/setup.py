from setuptools import setup, find_packages

setup(
    name="testospkg",
    version="0.0.2",
    # author="Your Name",
    # author_email="your.email@example.com",
    description="A simple Python package to say hello",
    # url="https://github.com/yourusername/hello-world-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

