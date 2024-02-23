from distutils.core import setup
from setuptools import find_namespace_packages

setup(name='drapi-lemur',
      package_dir={"": "src"},
      include_package_data=True,
      packages=find_namespace_packages(where="src"),
      version='1.0.22',
      description='Data Request API for the Integrated Data Repository Research Services of University of Florida.',
      long_description="Data Request API for the Integrated Data Repository Research Services of University of Florida.",
      author='Herman Autore',
      author_email='hf.autore+drapi@gmail.com',
      url='https://github.com/ChemGuy88/hermanCode/archive/refs/tags/v1.0.0.tar.gz',
      keywords=['CTSI',
                'Clinical and Translational Science Institute',
                'IDR',
                'Integrated Data Repository',
                'Integrated Data Repository Research Services',
                'ODSRI',
                'Office of Data Science and Research Implementation',
                'Shands',
                'Sloth 🦥',
                'UF',
                'UF Health',
                'UFHealth',
                'University of Florida'])
