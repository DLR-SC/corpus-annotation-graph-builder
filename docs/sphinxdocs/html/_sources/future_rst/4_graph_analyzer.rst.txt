.. role:: python(code)
   :language: python


Analyzers
=========


Our analyzer allow you to easily write converters and graph visualizations. The following sample allows you to see the connection between two corpus within one knowledge graph, convert that result to a :python:`NetworkX()` graph and visualize it using :python:`pyvis` using little code outside the actual arango query:

.. code-block:: python

    class CorpusDistanceAnalyzer(AnalyzerBase):
        def __init__(self, conf: Config):
            super().__init__(conf, run=False)

        def run(self, f_id, t_id):
            query = """FOR c_1 IN Corpus
        FILTER c_1._key==@f_id
        FOR c_2 IN Corpus
            FILTER c_2._key==@t_id
                FOR path IN ANY K_SHORTEST_PATHS c_1 TO c_2 GRAPH KnowledgeGraph
                    LIMIT 100
                    RETURN path"""
            aql = self.database.AQLQuery(query, bindVars={
                'f_id': f_id, 't_id': t_id}, rawResults=True)
            data = list(aql)
            g=self.visualize_graph(data)
            g.show() #if you are in a Jupyter Notebook
            # or you can directly create a NetworkX from your pahs:
            return self.create_networkx(data,weight_edges=True)
