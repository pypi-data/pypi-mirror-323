from setuptools import setup, find_packages

setup(
    name='matrix_operations_cuni',
    version='0.6.2',
    packages=find_packages(),
    install_requires=[

    ],
    author='Samo Kosik',
    author_email='samokosik@samokosik.com',
    description='A library for basic matrix operations.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.13',

)