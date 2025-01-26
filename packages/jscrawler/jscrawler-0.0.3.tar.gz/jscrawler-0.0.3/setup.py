from setuptools import setup, find_packages

def dependencies(imported_file):
    """ __Doc__ Handles dependencies """
    with open(imported_file) as file:
        return file.read().splitlines()

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="jscrawler",
    version="v0.0.3",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jscrawler=jscrawler.jscrawler:main',  # Adjust the import path for main
        ],
    },
    # install_requires=[],  # Add any dependencies if needed
    install_requires=dependencies('requirements.txt'),
    long_description=description,
    long_description_content_type="text/markdown",
)
