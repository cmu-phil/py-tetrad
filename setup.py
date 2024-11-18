import setuptools

with open('README.md', 'r') as fh:
    README = fh.read()

VERSION = '0.1.2'

setuptools.setup(
    name='py-tetrad',
    version=VERSION,
    author='Joseph Ramsey and Bryan Andrews',
    description='py-tetrad Python Package',
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'pandas',
        'JPype1',
    ],
    url='https://github.com/cmu-phil/py-tetrad',
    packages=setuptools.find_packages(include=['pytetrad', 'pytetrad.*']),
    package_data={
        'pytetrad': ['resources/*'], 
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
