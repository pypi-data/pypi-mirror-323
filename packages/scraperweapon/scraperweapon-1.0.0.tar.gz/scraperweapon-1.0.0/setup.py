from setuptools import setup, find_packages

setup(
    name='scraperweapon',  # The name of your library on PyPI
    version='1.0.0',
    description='A revolutionary web scraping library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # Use markdown for your README
    author='SumedhP',
    author_email='your.email@example.com',
    url='https://github.com/Sumedh1599/scraperweapon',  # Your GitHub repo URL
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'playwright',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
