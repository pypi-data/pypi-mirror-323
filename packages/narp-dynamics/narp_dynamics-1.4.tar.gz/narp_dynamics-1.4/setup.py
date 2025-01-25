from setuptools import setup

setup(
    name='narp-dynamics',
    version='1.4',
    packages=['narp_functions'],
    description='Implementation of NARP Pulses and Their Interaction Dynamics with Two-Level Systems',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Juan E. Ardila-García',
    author_email='juardilag@unal.edu.co',
    url='https://gitlab.com/juardilag/narp-dynaimics',
    install_requires=[
        'jax',
        'matplotlib',
        'cmap',
        'tqdm',
        'jupyter'
    ] 
)
