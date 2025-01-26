from setuptools import setup, find_packages

setup(
    name='Topsis_Kunal_102216002',  # Replace with your name and roll number
    version='2.0.0',
    author='Kunal',
    author_email='kbhalla600@gmail.com',
    description='A Python package to perform TOPSIS analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Kunal-code-u/Topsis-Kunal-102216002',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'topsis=Topsis_Kunal_102216002.topsis:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
