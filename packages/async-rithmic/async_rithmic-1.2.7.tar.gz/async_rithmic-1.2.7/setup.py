import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='async_rithmic',
    version='1.2.7',
    author='Mickael Burguet',
    description='Python API Integration with Rithmic Protocol Buffer API',
    keywords='python rithmic',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rundef/async_rithmic',
    project_urls={
        'Documentation': 'https://github.com/rundef/async_rithmic',
        'Bug Reports': 'https://github.com/rundef/async_rithmic/issues',
        'Source Code': 'https://github.com/rundef/async_rithmic',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': '.'},
    packages=setuptools.find_packages(where='.'),
    package_data={
        '': ['certificates/*'],
    },
    include_package_data=True,
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'websockets>=11.0,<15.0',
        'protobuf==4.25.4',
        'pytz>=2022.5',
        'tzlocal>=5.2',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest'],
    },
)
