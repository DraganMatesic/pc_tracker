from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pc_tracker',
      version='0.0.1',
      description='Framework for tracking activity on PC',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/DraganMatesic/pc_tracker',
      author='Dragan Matesic',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      install_requires=['pywin32', 'psutil', 'pynput', 'pysocks'],
      scripts=['scripts/manage.py']
      )
