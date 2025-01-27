from setuptools import setup, find_packages
import os

setup(
    name='kaededb',  # Package name (as you'll install it with pip - all lowercase is conventional)
    version='9',
    packages=find_packages(),  # Automatically find packages in the current directory (should find 'kaededb')
    install_requires=[
        'requests',
    ],
    author='Kento Hinode',
    author_email='cleaverdeath@gmail.com',
    description='KaedeDB Python Client Library',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/DarsheeeGamer/KaedeDB',  # Replace with your actual repository URL if you have one
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Or choose your license
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',  # Or other appropriate status
        'Intended Audience :: Developers',
        'Topic :: Database',
    ],
    python_requires='>=3.6',
)