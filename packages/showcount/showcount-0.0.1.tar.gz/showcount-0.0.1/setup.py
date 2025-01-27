import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="showcount",
    version="0.0.1",
    author="Henry Robbins",
    author_email="hw.robbins@gmail.com",
    description="Python package powering showcount.com.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/henryrobbins/showcount-python.git",
    packages=setuptools.find_packages(),
    license="GNU Affero General Public License v3.0",
    install_requires=[],
    extras_require={"dev": []},
    python_requires=">=3.11",
)
