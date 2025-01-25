from setuptools import setup

setup(
    name = 'narp-dynamics',
    version = '1.0',
    py_modules = ['narp_functions', 'narp_plotting_functions'],
    description = 'Implementation of NARP Pulses and Their Interaction Dynamics with Two-Level Systems',
    author = 'Juan E. Ardila-García',
    author_email = 'juardilag@unal.edu.co',
    url = 'https://gitlab.com/juardilag/narp-dynaimics',
    install_requires = [
        'jax',
        'matplotlib',
        'cmap',
        'tqdm'
    ]
)
