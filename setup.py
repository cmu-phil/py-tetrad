import setuptools

with open('README.md', 'r') as fh:
    README = fh.read()

VERSION = '0.1'

setuptools.setup(
    name='py-tetrad',
    version=VERSION,
    author='',
    description='py-tetrad Python Package',
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'pandas',
        'causal-learn'
    ],
    url='https://github.com/cmu-phil/py-tetrad',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
