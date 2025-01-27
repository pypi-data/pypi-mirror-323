from setuptools import setup, find_packages

setup(
    name='credex001',  # Name of your package
    version='0.1.0',
    packages=find_packages(),  # This automatically finds your packages
    install_requires=[  # List any dependencies
        'bs4',  # Required for your script
    ],
    author='a random dude',
    author_email='jcccadet3175@example.com',
    description='A tool to extract email and password pairs from HTML files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/credentials_extractor',  # Replace with actual URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update with your actual license
        'Operating System :: OS Independent',
    ],
)

#python setup.py sdist bdist_wheel