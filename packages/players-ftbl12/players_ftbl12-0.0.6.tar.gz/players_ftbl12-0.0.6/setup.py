from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 11',
  'Programming Language :: Python :: 3',
  'License :: OSI Approved :: MIT License',
]

setup(
  name='players_ftbl12',
  version='0.0.6',
  description='Takes player information from Transfermarkt',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
  long_description_content_type='text/markdown',
  url='https://github.com/y1ach/playersftbl12',
  author='Yach',
  author_email='yigitalicelik@hotmail.com',
  classifiers=classifiers,
  keywords='Football Players',
  packages=find_packages(),
  install_requires=['requests', 'beautifulsoup4'],
)
