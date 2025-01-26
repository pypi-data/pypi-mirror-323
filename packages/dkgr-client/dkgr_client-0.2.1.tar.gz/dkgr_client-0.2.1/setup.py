from setuptools import setup, find_packages

setup(
    name='dkgr_client',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    author='Akshay Behl',
    author_email='akshaybehl231@gmail.com',
    description='Wrapper for dkgr backend',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Captain-T2004/dkgr-client",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)