from setuptools import setup, find_namespace_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='neuraparse',
    version='0.3.6',
    author='Bayram EKER',
    author_email='eker600@gmail.com',
    description='Universal web scraper package for extracting web data efficiently',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bayrameker',
    packages=find_namespace_packages(include=['neuraparse*']),
    namespace_packages=['neuraparse'],
    install_requires=[
        'selenium>=4.0.0',
        'beautifulsoup4>=4.9.0',
        'requests>=2.25.0',
        'lxml>=4.6.0',
        'html5lib>=1.1',
        'undetected-chromedriver>=3.0.0',
        'urllib3>=1.25.0',
        'dataclasses; python_version<"3.7"',
        'readability-lxml>=0.8.1',  # <-- eklendi
    ],
    entry_points={
        'console_scripts': [
            'neuraparse-universal-scrape=neuraparse.universal_scraper.scraper:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
    license_files=('LICENSE',),
    keywords='web scraping, selenium, beautifulsoup, requests, lxml, undetected-chromedriver',
    project_urls={
        'Bug Reports': 'https://github.com/bayrameker',
        'Source': 'https://github.com/bayrameker',
        'Documentation': 'https://github.com/bayrameker',
    },
    include_package_data=True,
    package_data={
        'neuraparse': ['data/*.json'],
    },
)
