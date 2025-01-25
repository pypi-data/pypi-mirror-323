from setuptools import setup, find_packages

setup(
    name='102203166-topsis-stuti',
    version='0.1.0',
    author='Stuti Goyal',
    author_email='gstu180@gmail.com',
    description='A Python package to implement the TOPSIS method for multi-criteria decision analysis.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/stuti-go/topsis-package',
    packages=find_packages(),
    install_requires=['numpy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
