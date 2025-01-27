from setuptools import setup, find_packages
from kin_tokenizer.version import VERSION

with open('README.md') as f:
    description = f.read()


setup(
    name='alta_tokenizer',
    version=VERSION,
    author='Schadrack Niyibizi',
    author_email='niyibizischadrack@gmail.com',
    description='ALTA tokenizer for encoding and decoding Kinyarwanda language text',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nschadrack/Kin-Tokenizer',
    packages=find_packages(),
    keywords="Tokenizer, Kinyarwanda, ALTA Model",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        "regex>=2024.7.24",
        "setuptools>=72.2.0"
    ],
    package_data={
        'kin_tokenizer': ['data/*'],
    },
    include_package_data=True,
)