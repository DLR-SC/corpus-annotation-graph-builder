import setuptools
from setuptools import setup

setup(
    name='cag',
    version='0.9.0',
    description='This is a general framework to create arango db graphs',
    # url='',
    author='DLR',
    author_email='tobias.hecking@dlr.de',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['pyArango',
                      'python-arango',
                      'nltk',
                      'networkx',
                      'pyvis',
                      'tomli >= 1.1.0',
                      'spacy>=3.4',
                      # for spacy - it uses soft_unicode which was removed from version > 2.0.1
                      'markupsafe<=2.0.1',
                      'empath>=0.89'
                      ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={"configs": ["*.toml"]},
)
