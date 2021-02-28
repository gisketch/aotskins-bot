from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(name='Reto',
      version='1.6',
      description='Vote-handling Discord bot! React on messages, give points to the best commenters, and Star stuff to put it in the Best Of channel.',
      long_description=long_description,
      url='http://github.com/despedite/reto',
      author='Despedite',
      author_email='hi@erik.games',
      license='Apache License 2.0',
      install_requires=[
          'discord.py',
          'pyfiglet',
          'tinydb',
          'aiofiles',
          'tinydb-encrypted-jsonstorage'
      ],
      zip_safe=False)