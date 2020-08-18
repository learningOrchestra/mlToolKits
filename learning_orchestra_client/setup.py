import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="learning_orchestra_client",
    version="0.3",
    author="Gabriel Ribeiro",
    author_email="gabbriel.rribeiro@gmail.com",
    description="Learning Orchestra client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com//riibeirogabriel/learningOrchestra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
