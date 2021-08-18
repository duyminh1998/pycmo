from setuptools import setup

description = """PyCMO"""

setup(
    name='PyCMO',
    version='1.0.0',
    description='Command Modern Operations Reinforcement Learning Environment.',
    long_description=description,
    author='Minh Hua',
    author_email='mhua2@jh.edu',
    license='MIT License',
    keywords='Command Modern Operations AI',
    url='https://github.com/duyminh1998/pycmo',
    packages=[
        'pycmo',
        'pycmo.agents',
        'pycmo.bin',
        'pycmo.env',
        'pycmo.lib'
    ],
    install_requires=[
        'numpy>=1.10',
        'xmltodict==0.12.0'
    ],
)