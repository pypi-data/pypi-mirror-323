from setuptools import setup, find_packages

setup(
    name='mongodb_controller',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'pymongo>=4.10.1',
        'pandas>=2.2.3',
        'python-dotenv>=1.0.0',
        'aws-s3-controller>=0.6.4',
        'shining-pebbles>=0.2.72',
    ],
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A Python module for managing fund time series data using MongoDB',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nailen1/mongodb_controller.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    keywords='mongodb database fund time-series data-management',
)
