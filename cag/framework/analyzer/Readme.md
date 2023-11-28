## Query Builder
### Overview
The Query Builder can be used to build an ArangoDB query (AQL query) to query a given graph pattern. The graph pattern is defined in a JSON structure (see below).
### Usage
##### Database Configuration
In order to connect to the database, please provide the database connection details in a configuration object of type `cag.utils.config.Config`:

    my_config = Config(
	    url=<host>:<port>,
	    user=<username>,
	    password=<password>,
	    database=<database name>,
	    graph=<database graph>
    )

##### Database Configuration
Furthermore, it is required to specify the graph pattern, that should be queried, as a json object. The graph pattern object is of type `GraphData` and looks like this:

*GraphData:*
Contains two lists.

    nodes: list[NodeDTO]
    edges: list[EdgeDTO]
    
*NodeDTO*:
Each node must have an id (can be arbitrary chosen), a collection name (must match to a vertex collection name in the database) and filter properties, provided as a list of objects.

    id: str
    collection: str
    userData: list[UserData]
    
*EdgeDTO*:
Each edge must have an id (can be arbitrary chosen), a source and target (which reference the corresponding node ids), a collection name (must match to an edge collection name in the database) and filter properties, provided as a list of objects.

    id: str
    source: str
    target: str
    name: str
    userData: list[UserData]
    
*UserData*:
Userdata defines properties that documents should be filtered with (e.g. to filter only documents with a certain property). If any conditions are provided, they must contain the attribute name (i.e. property name of the collection in the database), its data type ("text", "number", "date" or "datetime"), the operator to use and the filter value.

    attribute: str
    attributeType: str
    operator: OperatorEnum
    value: str
    
*OperatorEnum*:
Within userData, the operator can be of any of the following values:

    CONTAINS
    CONTAINS_NOT
    EQUALS 
    EQUALS_NOT
    ALPHABETIC_CONTAINS
    ALPHABETIC_CONTAINS_NOT
    ALPHABETIC_STARTS_WITH
    ALPHABETIC_ENDS_WITH
    NUMERIC_EQUALS
    NUMERIC_SMALLER_THAN
    NUMERIC_SMALLER_OR_EQUAL
    NUMERIC_LARGER_THAN
    NUMERIC_LARGER_OR_EQUAL
    DATE_SMALLER_THAN
    DATE_SMALLER_OR_EQUAL
    DATE_LARGER_THAN
    DATE_LARGER_OR_EQUAL

A valid example of `graph_data` could look like this:

    {
    	"nodes":[
    	    {
    			"id":"0",
    			"collection":"Person",
    			"userData":[
    				{
    					"attribute":"name",
    					"attributeType":"text",
    					"operator": "alphabetic_contains",
    					"value":"Bob",
    				}
    			]
    		},
    		{
    			"id":"1",
    			"collection":"Document",
    			"userData":[
    				{
    					"attribute":"title",
    					"attributeType":"text",
    					"operator": "alphabetic_contains",
    					"value":"Climate Change",
    				}
    			]
    		}
    	],
    	"edges":[
    		{
    		"id":"0",
    		"source":"0",
    		"target":"1",
    		"name":"Wrote",
    		"userData": [
    			{
    				"attribute":"timestamp",
    				"attributeType":"datetime",
    				"operator": "date_smaller_than",
    				"value":"2023-11-24T23:00:00.000Z",
    			}
    		]
    	}
    	],
    }
It indicates that a Person whose name contains the string "Bob" wrote a Document whose title contains "Climate Change" before the date 2023-11-24.

##### Query Generation
Next create a new QueryBuilder object using this configuration:

    query_builder = QueryBuilder(my_config)
    
Finally, call the `_generate_aql_graph_query()` function to generate the AQL query, ready to be executed:

    aql_query, bind_vars = query_builder.generate_aql_graph_query(graph_data, max_start_nodes=444, max_paths=555)

`max_start_nodes`   denotes the maximum number of documents to be obtained in the first part of the query (see LIMIT 444 below). `max_paths` denotes the maximum number of paths to be obtained, before the graph traversal halts (see LIMIT 555 below).
  
`aql_query` contains the actual AQL query. It is parameterized, meaning that field names and values are replaced with respective parameter names (e.g. "@field_xy"). The corresponding mapping is stored in `bind_vars`.

A generated query typically looks like the following example, corresponding to the above example of `graph_data`:

    LET doc_0 = FLATTEN(
        FOR p IN Person
            FILTER CONTAINS(LOWER(p.@field_bvsRP4nK2b), LOWER(@value_F83IiG4DIU)) /* "name" contains "Bob" */
            LIMIT 444
            RETURN doc
    )
    
    LET start_nodes = UNION(doc_0, [])
    
    /* For each start node, start finding a path */
    FOR start_node IN start_nodes
        /* Each Edge has the corresponding direction specified to make querying faster */
        FOR v, e, p IN @min..@max ANY start_node OUTBOUND Wrote
        OPTIONS { vertexCollections: @vertex_collections, edgeCollections: @edge_collections }
            FILTER (
                (
                    (
			            IS_SAME_COLLECTION(p.vertices[0], @w2SVniSu3W) /* Vertex at index 0 is of "Person" collection */
					) 
                    AND
                    (
                        CONTAINS(LOWER(p.vertices[0].@field_5E8ggp4h39), LOWER(@value_IiTNm4EVbU)) /* "name" contains "Bob" */
                    )
                    AND
                    (
                        p.edges[0].@field_ktvTx42cK9 < DATE_ISO8601(@value_7sOZ02Ctnf) /* "timestamp" before "2023-11-24T23:00:00.000Z" */
                    )
                    AND
                    (
	                    IS_SAME_COLLECTION(p.vertices[1], @DxJ8jHKDO0) /* Vertex at index 1 is of "Document" collection */
	                ) 
                    AND
                    (
                        CONTAINS(LOWER(p.vertices[1].@field_5x0FjrXzek), LOWER(@value_llAcaYxkIU)) /* "title" contains "Climate Change" */
                    )
                )
            )
            LIMIT 555
            RETURN p

##### Query Execution
To execute the generated query, call `execute_aql_query()`:

    query_result = query_builder.execute_aql_query(aql_query, bind_vars)

The query result is of type `arango.cursor.Cursor` (see [docs](https://python-driver-for-arangodb.readthedocs.io/_/downloads/en/dev/pdf/))



