from setuptools import setup, find_packages

setup(
    name='BeginnerNN',
    version='1.0.0',
    description='A beginner-friendly neural network library using PyTorch and NumPy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zian Conradie',
    author_email='zianconradie@gmail.com',
    url='https://github.com/MicrolabsZ/BeginnerNN',
    packages=find_packages(),
    install_requires=[
        'torch>=1.7.0',
        'numpy>=1.18.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7,<=3.10',  # Recommend 3.7 to 3.10 for beginners
    package_dir={'': '.'},  # Fixes egg_base error by indicating current directory
)
