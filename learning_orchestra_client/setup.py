import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="learning_orchestra_client",
    version="1.0.1",
    author="Gabriel Ribeiro",
    author_email="gabbriel.rribeiro@gmail.com",
    description="Learning Orchestra client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com//riibeirogabriel/learningOrchestra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
