from setuptools import setup, find_packages

setup(
    name='gini-py',
    version='0.1.7',
    author='Roba Olana',
    author_email='support@gini.works',
    description='Python SDK to interact with Gini (https://gini.works)',
    long_description='Python SDK to interact with [Gini](https://www.gini.works)',
    long_description_content_type='text/markdown',
    url='https://github.com/Works-By-Gini/gini-py', 
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License', 
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'pycryptodome>=3.19.0',  # For encryption
        'requests>=2.31.0',       # For HTTP requests
        'pydantic>=2.0.0',       # For data validation
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
)