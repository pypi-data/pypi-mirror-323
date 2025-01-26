from setuptools import setup, find_packages

setup(
    name='wordcraft',
    version='0.1',
    packages=find_packages(),
    description='A Library for Training Language Models with LSTM in TensorFlow',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='AKM Korishee Apurbo',
    author_email='bandinvisible8@gmail.com',
    url='https://github.com/IMApurbo/wordcraft',  # Replace with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'tensorflow>=2.0.0',  # For TensorFlow (LSTM)
        'numpy>=1.19.0',  # For numerical operations
        'pickle-mixin>=1.0.0',  # For object serialization
    ],
    python_requires='>=3.6',  # Specify the minimum required Python version
    include_package_data=True,
)
