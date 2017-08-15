from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.3.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [
    x.strip()
    for x
    in all_reqs
    if 'git+' not in x
]
dependency_links = [
    x.strip().replace('git+', '')
    for x
    in all_reqs
    if x.startswith('git+')
]

setup(
    name='phix',
    version=__version__,
    author='Kit La Touche',
    author_email='kit@transneptune.net',
    description='Make writing your Sphinx docs a little easier.',
    long_description=long_description,
    url='https://github.com/wlonk/phix',
    download_url='https://github.com/wlonk/phix/tarball/' + __version__,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    keywords=['Sphinx'],
    packages=find_packages(exclude=['docs', 'tests*']),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'phix=phix:main',
        ],
    },
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
)
