# setup.py

from setuptools import setup, find_packages

setup(
    name='python_cache_manager',
    version='0.1.0',
    description='A cache manager supporting Redis and Memcached',
    author='mstfsu',
    author_email='su.mustafa@hotmail.com',
    packages=find_packages(),
    install_requires=[
        'redis==4.4.0',
        'pymemcache==4.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
