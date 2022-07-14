from setuptools import setup

setup(
    name='graph_framework',
    version='0.3.0',
    description='This is a general framework to create arango db graphs',
    # url='',
    author='DLR',
    author_email='tobias.hecking@dlr.de',
    license='MIT',
    packages=['graph_framework',
              'graph_framework.components',
              'graph_framework.graph',
              'graph_framework.utils'],
    install_requires=['pyArango',
                      'python-arango',
                      ],
)
