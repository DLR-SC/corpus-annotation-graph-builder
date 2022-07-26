from setuptools import setup

setup(
    name='cag',
    version='0.6.0',
    description='This is a general framework to create arango db graphs',
    # url='',
    author='DLR',
    author_email='tobias.hecking@dlr.de',
    license='MIT',
    packages=['cag.graph_framework',
              'cag.graph_framework.components',
              'cag.graph_framework.graph',
              'cag.utils',
              'cag.view_wrapper'],
    install_requires=['pyArango',
                      'python-arango',
                      'nltk'
                      ],
    classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
      ],
      zip_safe=False,


)
