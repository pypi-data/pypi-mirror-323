from setuptools import setup, find_packages

setup(
    name='fineweb-tools',
    version='0.0.6',
    license='Apache V2',
    description='Tools for preprocessing, analyzing, and distilling FineWeb data.',
    author='Jordan Wolfgang Klein',
    author_email='jwklein14@gmail.com',
    url='https://github.com/user/Lone-Wolfgang',
    keywords=['FineWeb'],
    install_requires=[
        'polars',
        'huggingface-hub',
        'tld',
        'typing',
        'beautifulsoup4',
        'selenium',
        'datasets'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    packages=find_packages(),
    include_package_data=True
)
