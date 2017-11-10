try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
]

REQUIREMENTS = [
    'itsdangerous',
    'requests',
    'simplejson',
    'werkzeug',
]
setup(
    name='wRESTler',
    author='Tomasz Rybarczyk',
    author_email='paluho@gmail.com',
    classifiers=CLASSIFIERS,
    description='Set of utilities for werkzeug REST services',
    install_requires=REQUIREMENTS,
    url='https://github.com/paluh/wrestler',
    packages=['wrestler'],
    zip_safe=False,
    test_suite='wrestler.tests.test_suite',
    version = '0.0.2',
)
