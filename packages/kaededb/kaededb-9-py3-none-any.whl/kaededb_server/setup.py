# kaededb_server/setup.py
from setuptools import setup, find_packages

setup(
    name='KaedeDB-Server',
    version='9',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'cryptography',
    ],
    entry_points={
        'console_scripts': [
            'kaededb = kaededb_server.api:main',
        ],
    },
    author='Kento Hinode',      # Replace with your name
    author_email='cleaverdeath@gmail.com', # Replace with your email
    description='KaedeDB Server component',
    long_description="KaedeDB Server - Lightweight File-Based Database with REST API",
    long_description_content_type='text/plain',
    url='https://github.com/DarsheeeGamer/KaedeDB', # Replace with your repository URL if you have one
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License', # Choose a license if you have one (e.g., MIT)
        'Development Status :: 3 - Alpha', # Or other appropriate status
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
    python_requires='>=3.6',
)