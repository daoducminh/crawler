# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name='crawler',
    version='1.0',
    author='minhdao',
    description='Crawler Project',
    packages=find_packages(exclude=[
        'docs',
        'tests',
        'static',
        'templates',
        '.gitignore',
        'README.md'
    ]),
    entry_points={'scrapy': ['settings = crawler.settings']},
    install_requires=[
        'scrapy'
    ]
)
