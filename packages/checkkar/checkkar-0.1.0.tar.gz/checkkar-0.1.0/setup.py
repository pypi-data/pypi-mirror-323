from setuptools import setup, find_packages

setup(
    name='checkkar',
    version='0.1.0',
    packages=find_packages(),
    description='A simple library to check if a number is 69',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Vaibhav Murarka',
    author_email='vaibhavmurarka14@gmail.com.com',
    url='https://github.com/VaibhavMurarka/checkkar',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
