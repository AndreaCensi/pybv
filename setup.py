from setuptools import setup


setup(name='pybv',
      version='0.1',
      package_dir={'':'src'},
      py_modules=['pybv'],
	  install_requires=['PIL', 'jsonstream', 'simplejson'],
	 #install_requires = ['pycairo','PIL','jsonstream', 'simplejson'],
#      py_modules=find_packages()
      )
