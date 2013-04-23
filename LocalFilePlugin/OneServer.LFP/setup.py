import os
from setuptools import find_packages, setup

setup(name='LocalFilePlugin.py',
      version='0.1.0',
	  description='LocalFilePlugin handles files for the oneserver',
	  keywords='FileHandler metadata database',
    zip_safe=False,
    include_package_data=True,
	  install_requires=[
	#		'Python >= 2.7',
			'pyutilib.component.core',
			'pymediainfo'
				],
	  classifiers=[
			"Development Status :: 3 - Alpha",
			"Topic :: Plugin"
				],
	  packages=find_packages(),
	  namespace_packages=['LocalFilePlugin'],
	  entry_points={
		'OneServer' : [
			'LocalFilePlugin = LocalFilePlugin.LocalFilePlugin:LocalFilePlugin',
		],
	  }

)

