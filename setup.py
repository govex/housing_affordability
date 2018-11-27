from setuptools import setup, find_packages

setup(name='housing-affordability',
      version='0.1',
      description='GovEx Housing Affordability Django App',
      url='',
      author='Sara Bertran de Lis, Ben Miller',
      author_email='sbertran@jhu.edu, benjamin.miller@jhu.edu',
      license='',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'scipy',
          'pandas',
          'requests',
          'SQLAlchemy',
          'psycopg2',
          'us',
          'census',
          'plotly'
      ],
      include_package_data=True,
      zip_safe=False)
