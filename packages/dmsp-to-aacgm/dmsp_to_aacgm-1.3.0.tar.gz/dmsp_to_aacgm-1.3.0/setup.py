from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name = 'dmsp-to-aacgm',
    version = '1.3.0',
    author = "Carson O'Ffill",
    author_email = 'offillcarson@gmail.com',
    license = 'MIT',
    description = 'A CLI tool to convert geomagnetic coordinates in DMSP data files to AACGM coordinates.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/karzunn/dmsp-to-aacgm',
    py_modules = ['dmsp_to_aacgm'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.12',
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        dmsp-to-aacgm=dmsp_to_aacgm.cli:cli
    '''
)