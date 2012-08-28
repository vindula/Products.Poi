from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('Products', 'Poi', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()

readmefile = open(os.path.join('Products', 'Poi', 'README.txt'))
readme = readmefile.read().strip()
readmefile.close()

historyfile = open(os.path.join('Products', 'Poi', 'HISTORY.txt'))
history = historyfile.read().strip()
historyfile.close()

long_description = readme + "\n\n" + history

setup(name='Products.Poi',
      version=version,
      description="Poi: A friendly issue tracker",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Martin Aspeli',
      author_email='plone-users@lists.sourceforge.net',
      url='http://plone.org/products/poi',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone>=4.0b1',
          'Products.AddRemoveWidget>=1.4.2',
          'Products.DataGridField>=1.8b1',
          'collective.watcherlist>=0.2',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
