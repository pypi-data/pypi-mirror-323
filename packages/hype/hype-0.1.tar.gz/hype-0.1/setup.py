import re

try:
    import setuptools
except ImportError:
    import distutils.core
    setup = distutils.core.setup
else:
    setup = setuptools.setup

setup(
    name='hype',
    version=(
        re
        .compile(r".*__version__ = '(.*?)'", re.S)
        .match(open('hype/__init__.py').read())
        .group(1)
    ),
    url='https://github.com/balanced/hype/',
    license=open('LICENSE').read(),
    author='balancedpayments.com',
    author_email='dev@balancedpayments.com',
    description='Yet another resource mapper.',
    long_description=(
        open('README.rst').read() + '\n\n' +
        open('HISTORY.rst').read()
    ),
    py_modules=['hype'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    tests_require=[
    ],
    install_requires=[
    ],
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
