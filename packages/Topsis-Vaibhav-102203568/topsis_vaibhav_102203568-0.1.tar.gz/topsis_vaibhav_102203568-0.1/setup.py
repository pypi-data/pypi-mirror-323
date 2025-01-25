from setuptools import setup, find_packages

setup(
    name='Topsis-Vaibhav-102203568',
    version='0.1',
    description='A Python package for Topsis implementation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Vaibhav Baldeva',
    author_email='vbaldeva_be22@thapar.edu',
    url='https://github.com/VBaldeva/Topsis-YourName-RollNumber',
    packages=find_packages(),
    install_requires=['numpy', 'pandas'],
    entry_points={
        'console_scripts': [
            'topsis=topsis_package.topsis:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
