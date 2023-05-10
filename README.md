

<h1 align="center">Welcome to the Corpus Annotation Graph Builder <code>(CAG)</code> </h1>

<p align="center">
 <a href="https://pypi.org/project/cag/"><img src="https://badge.fury.io/py/cag.svg" alt="Badge: PyPI version" height="18"></a>
  <a href="https://img.shields.io/badge/Made%20with-Python-1f425f.svg">
    <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Badge: Made with Python"/>
  </a>
  

  <a href="https://open.vscode.dev/DLR-SC/corpus-annotation-graph-builder">
    <img alt="Badge: Open in VSCode" src="https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=open%20in%20visual%20studio%20code&labelColor=2c2c32&color=007acc&logoColor=007acc" target="_blank" />
  </a>
     <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Badge: Black" height="18"></a>
<a href="https://zenodo.org/badge/latestdoi/572124344"><img src="https://zenodo.org/badge/572124344.svg" alt="DOI"></a>
 <a href="https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/master/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-yellow.svg" target="_blank" />
  </a>
    <a href="https://twitter.com/dlr_software">
    <img alt="Twitter: DLR Software" src="https://img.shields.io/twitter/follow/dlr_software.svg?style=social" target="_blank" />
  </a>
</p>


> `cag` is a Python Library offering an architectural framework to employ the build-annotate pattern when building Graphs.

---



[Official Documentation](https://cagraph.info/).

**Corpus Annotation Graph builder (CAG)**  is an *architectural framework* that employs the *build-and-annotate* pattern for creating a graph. CAG is built on top of [ArangoDB](https://www.arangodb.com) and its Python drivers ([PyArango](https://pyarango.readthedocs.io/en/latest/)). The *build-and-annotate* pattern consists of two phases (see Figure below): (1) data is collected from different sources (e.g., publication databases, online encyclopedias, news feeds, web portals, electronic libraries, repositories, media platforms) and preprocessed to build the core nodes, which we call *Objects of Interest*. The component responsible for this phase is the **Graph-Creator**. (2) Annotations are extracted from the OOIs, and corresponding annotation nodes are created and linked to the core nodes. The component dealing with this phase is the **Graph-Annotator**.


![cag](https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/main/docs/cag.png?raw=true)


This framework aims to offer researchers a flexible but unified and reproducible way of organizing and maintaining their interlinked document collections in a Corpus Annotation Graph. 

## Installation

### Direct install via pip 

The package can also be installed directly via pip.
```
pip install cag
```

This will allow you to use the module **`cag`** from any python script locally. The two main packages are **`cag.framework`** and **`cag.view_wrapper`**.


### Manual cloning
Clone the repository, go to the root folder and then run:

```
pip install -e .
```

## Citation
Please cite us in case you use CAG

    @inproceedings{el-baff-etal-2023-corpus,
      title = "Corpus Annotation Graph Builder ({CAG}): An Architectural Framework to Create and Annotate a Multi-source Graph",
      author = "El Baff, Roxanne  and
        Hecking, Tobias  and
        Hamm, Andreas  and
        Korte, Jasper W.  and
        Bartsch, Sabine",
      booktitle = "Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations",
      month = may,
      year = "2023",
      address = "Dubrovnik, Croatia",
      publisher = "Association for Computational Linguistics",
      url = "https://aclanthology.org/2023.eacl-demo.28",
      pages = "248--255"
    }


## Usage
* After the installation, a project scaffold can be created with the command `cag start-project`
* Graph Creation [[jupyter notebook](https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/main/examples/1_create_graph.ipynb)]
* Graph Annotation [[jupyter notebook](https://github.com/DLR-SC/corpus-annotation-graph-builder/blob/main/examples/2_annotate_graph.ipynb)]



## Zenodo refs

* v1.5.0 [![DOI](https://zenodo.org/badge/572124344.svg)](https://zenodo.org/badge/latestdoi/572124344)
* v1.4.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7701921.svg)](https://doi.org/10.5281/zenodo.7701921)


