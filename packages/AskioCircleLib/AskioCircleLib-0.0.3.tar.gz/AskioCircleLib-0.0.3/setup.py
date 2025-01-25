from setuptools import setup, find_packages
 
setup(
  name='AskioCircleLib',
  version='0.0.3',
  description='circle class',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Askio',
  author_email='legoask@gmail.com',
  keywords='circle', 
  packages=find_packages(),
  install_requires=['pygame'] 
)