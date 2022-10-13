import setuptools
from setuptools import setup

setup(
    name='cag',
    version='0.11.0',
    description='This is a general framework to create arango db graphs, annot',
    # url='',
    author='DLR',
    author_email='tobias.hecking@dlr.de, roxanne.elbaff@dlr.de',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['dataclasses>=0.6',
                    'spacy>=3.4.1',
                    'spacy_arguing_lexicon>=0.0.3',
                    'empath>=0.89',
                    'pytest>=7.1.2',
                    'networkx>=2.8.5',
                    'nltk>=3.4.5',
                    'pyvis>=0.2.1',
                    'tqdm>=4.43.0',
                    'python-arango>=7.4.1',
                    #'arango==0.2.1',
                    'pyArango>=2.0.1',
                    'tomli>=2.0.1'
                      ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    zip_safe=False
)
