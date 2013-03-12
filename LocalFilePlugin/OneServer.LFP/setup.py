from setuptools import find_packages, setup

setup(name='LocalFilePlugin.py',
      version='0.1.0',
      description='LocalFilePlugin handles files for the oneserver',
      install_requires=[
			'Python >= 2.7',
			'pymediainfo'
                       ],
      classifiers=[
			"Development Status :: 3 - Alpha",
			"Topic :: Plugin"
      ],
      entry_points = """
			[oneserver.plugins]
			LocalFilePlugin = OneServer.LFP.LocalFilePlugin.LocalFilePlugin
			""",
	  keywords='FileHandler metadata database',
	  packages = find_packages()
)

