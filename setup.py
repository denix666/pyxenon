from setuptools import setup, find_packages

setup(name='pyxenon',
      version='0.7',
      description='Preview for xenon game written iin python',
      url='https://github.com/denix666/pyxenon',
      author='Denis Salmanovich',
      author_email='denis.salmanovich@gmail.com',
      include_package_data=True,
      license='GPLv3',
      packages=find_packages(),
      package_data={
        '': ['*.ttf', '*.ico', '*.jpg', '*.png', '*.ogg', '*.mp3', '*.wav', '*.json'],
      },
      requires=[
        'python (>=3.8.0)',
        'pygame (>=2.1.2)',
        ],
      zip_safe=False,
      entry_points={
          'console_scripts': ['pyxenon=pyxenon.__main__'],
      }
      )
