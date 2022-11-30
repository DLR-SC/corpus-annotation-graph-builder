import setuptools
from setuptools import setup
__version__  ="0.5.5"
URL = 'https://github.com/DLR-SC/corpus-annotation-graph-builder'
setup(
    name='cag',
    version=__version__,
    description='This is a general framework to create arango db graphs and annotate them.',
    url=URL,
    author='DLR',
    author_email='roxanne.elbaff@dlr.de, tobias.hecking@dlr.de',
    license='MIT',
    download_url=f'{URL}/archive/{__version__}.tar.gz',
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    keywords=['graph', 'architectural framework', 'graph creator', 'graph annotator'],
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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': ['cag=cag.cli:app'],
    },
    zip_safe=False
)
