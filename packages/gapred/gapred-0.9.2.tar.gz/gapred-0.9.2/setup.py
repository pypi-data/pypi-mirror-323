from setuptools import setup, find_packages

setup(
    name="gapred",  # Library name
    version="0.9.2",  # Initial version
    description="Self-made ML framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/radhofan/Gapred",  # Replace with your repository
    packages=find_packages(),
    install_requires=["numpy"],  # Dependencies
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
