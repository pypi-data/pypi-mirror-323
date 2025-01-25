from setuptools import setup, find_packages


with open("README.md", "r") as file:
	description = file.read()

setup(
	name="percents",
	version="1.2.1",
	packages=find_packages(),
	install_requires=[],
	long_description=description,
	long_description_content_type="text/markdown",
)
