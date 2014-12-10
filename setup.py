from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


authors = [
    'Fabio Menegazzo <menegazzo@gmail.com>',
    'Bruno Oliveira <nicoddemus@gmail.com>',
]

setup(
    name='bender-hooks',
    version='0.1.0',
    py_modules=['bender_hooks'],

    # PyPI meta-data.
    author=', '.join(authors),
    description='Create hooks as decorators.',
    long_description=open('README.rst').read(),
    license='LGPLv3',
    keywords='hook, decorator, interface',
    url='https://github.com/bender-bot/bender-hooks',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    # tests
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
