"""Django ForeignKey that links to one of several specified models"""

from setuptools import setup, find_packages

setup(
	name='django-multiforeignkey',
	version='0.0.1',
	url='https://github.com/IlyaSemenov/django-multiforeignkey',
	license='BSD',
	author='Ilya Semenov',
	author_email='ilya@semenov.co',
	description=__doc__,
	long_description=open('README.rst').read(),
	packages=find_packages(),
	include_package_data=True,
	install_requires=['Django>=1.7'],
	classifiers=[],
)
