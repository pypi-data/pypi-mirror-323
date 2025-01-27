from setuptools import setup, find_packages

setup(
    name='sophnet',
    version='0.0.1',
    description='SOPHON.NET SDK for interacting with APIs',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
         'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
