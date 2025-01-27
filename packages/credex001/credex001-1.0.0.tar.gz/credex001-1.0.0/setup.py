from setuptools import setup, find_packages

setup(
    name='credex001',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'bs4',
    ],
    author='a random dude',
    author_email='jcccadet3175@example.com',
    description='A tool to extract email and password pairs from HTML files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

#python setup.py sdist bdist_wheel