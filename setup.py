from setuptools import setup, find_packages

setup(name='pc_tracker',
      version='0.0.0',
      description='Framework for tracking events on PC',
      author='Dragan Matesic',
      author_email='dragan.matesic@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires=['pywin32', 'psutil', 'pynput', 'pysocks'],
      )
