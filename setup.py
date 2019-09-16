from setuptools import setup
import os

setup(
    name='bw2io',
    version="0.7.7",
    packages=[
        'bw2io',
        'bw2io.data',
        'bw2io.export',
        'bw2io.extractors',
        'bw2io.importers',
        'bw2io.strategies',
    ],
    package_data={'bw2io': [
        "data/*.*",
        "data/lci/*.*",
        "data/lcia/*.*",
    ]},
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license="BSD 3-clause",
    install_requires=[
        "bw2calc>=1.7.4",
        "bw2data>=3.5.1",
        "lxml",
        "numpy",
        "psutil",
        "pyprind",
        "scipy",
        "stats_arrays",
        "unidecode",
        "voluptuous",
        "xlsxwriter",
        "xlrd",
    ],
    url="https://bitbucket.org/cmutel/brightway2-io",
    long_description=open('README.rst').read(),
    description=('Tools for importing and export life cycle inventory databases'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
