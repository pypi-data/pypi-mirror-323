from setuptools import setup, find_packages

setup(
    name='Topsis-Rijul-102217207',  # Replace with your actual name and roll number
    version='1.0.0',  # Follow semantic versioning
    author='Rijul Bansal',
    author_email='your-email@example.com',  # Replace with your email
    description='A Python package for implementing the TOPSIS decision-making method',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.1.0',
        'numpy>=1.19.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
