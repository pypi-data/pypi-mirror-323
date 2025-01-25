import setuptools

REQUIRED_PACKAGES = [
"numpy >= 1.26.4",
"matplotlib >= 3.8.4",
"pandas >= 2.2.2",
"scikit-learn >= 1.4.2"
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="radnn",
    version="0.0.1",
    author="Pantelis I. Kaplanoglou",
    author_email="pikaplanoglou@ihu.gr",
    description="Rapid Deep Neural Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pikaplan/radnn",
    license="MIT",
    packages=setuptools.find_packages(),
	install_requires=REQUIRED_PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)