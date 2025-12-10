"""
dj-payfast: Django PayFast Integration Library
"""
import os
from setuptools import setup, find_packages

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Read version from package
def get_version():
    with open('payfast/__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='dj-payfast',
    version=get_version(),
    author='Carrington Muleya',
    author_email='mcrn96m@gmail.com',
    description='Django PayFast integration library for South African payments',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/carrington-dev/dj-payfast',
    project_urls={
        'Bug Reports': 'https://github.com/carrington-dev/dj-payfast/issues',
        'Source': 'https://github.com/carrington-dev/dj-payfast',
        'Documentation': 'https://carrington-dev.github.io/dj-payfast/',
    },
    packages=find_packages(exclude=['tests*', 'docs*', 'example_project*']),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-django>=4.5.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'isort>=5.10.0',
            'mypy>=0.990',
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-copybutton>=0.5.0',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    keywords='django payfast payment gateway south-africa payments',
    license='MIT',
    zip_safe=False,
)