from setuptools import setup, find_packages

setup(
    name='tamilan',  # Your package name
    version='0.1.7',
    packages=find_packages(where='src'),  # Specify the source directory
    package_dir={'': 'src'},  # This will include your twosum.py file
    install_requires=[
        "requests",
        # Add any dependencies your module needs
    ],
    author='Sivasaran',
    author_email='sivasaran354@gmail.com',
    description='This module is for Gemini Api Intraction, TwoSum operations and subsequence checks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sivasarans/2sum',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
)
