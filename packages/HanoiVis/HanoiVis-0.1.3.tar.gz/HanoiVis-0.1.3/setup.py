from distutils.core import setup

setup(
    name='HanoiVis',
    version='0.1.3',
    author='Arvind Olag',
    author_email='arvindolag@gmail.com',
    packages=['hanoivis', 'hanoivis.test'],
    scripts=['hanoivis/hanoivis.py'],
    url='http://pypi.python.org/pypi/HanoiVis/',
    license='LICENSE.txt',
    description='Tower of Hanoi visualiser',
    long_description=open('README.rst').read()
)