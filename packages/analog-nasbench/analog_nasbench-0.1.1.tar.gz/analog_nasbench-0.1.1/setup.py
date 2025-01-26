from setuptools import setup, find_packages

setup(
    name='analog-nasbench',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'analog-nasbench': ['benchmark_data.csv'],
    },
    data_files=[('nalog-nasbench', ['analognasbench/benchmark_data.csv'])],
    install_requires=[
        'pandas',
        'numpy',
    ],
    author='Aniss Bessalah',
    author_email='ka_bessalah@esi.dz',
    description='A package for querying NAS benchmark with analog hardware metrics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/anissbslh/analognasbench',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)