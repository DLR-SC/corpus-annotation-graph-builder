### FLOW QUERIES ###
# Get start nodes without using views
GET_DOCUMENTS_FILTERS_USING_COLLECTION = (
    '\n' +
    'LET {query_var} = FLATTEN( ' +
    '\n\tFOR {loop_var} IN {collection} ' +
    '\t{filters} ' +
    '\n\t{limit} ' +
    '\n\tRETURN doc ' +
    '\n)'
)

# Get start nodes using views
GET_DOCUMENTS_FILTERS_USING_VIEW = (
    '\n' +
    'LET {query_var} = FLATTEN( ' +
    '\n\tFOR {loop_var} IN {view} ' +
    '\t{filters} ' +
    '\n\t{limit} ' +
    '\n\tRETURN doc ' +
    '\n)'
)

# Combine multiple start nodes queries
UNION_START_NODES = (
    '\n' +
    'LET {var} = UNION({lists}, []) '
)

# Perform graph traversal
GET_GRAPH = (
    '{start_nodes_aql_query} ' +
    '\n\n/* For each start node, start finding a path */ ' +
    '\nFOR start_node IN {start_nodes_var} ' +
    '\n\t/* Each Edge has the corresponding direction specified to make querying faster */ ' +
    '\n\tFOR v, e, p IN @min..@max {base_direction} start_node {edge_directions} {graph_stmt} ' +
    '\n\tOPTIONS {{ vertexCollections: @vertex_collections, edgeCollections: @edge_collections }} ' +
    '\n\t\t{path_filters} ' +
    '\n\t{limit} ' +
    '\n\tRETURN p'
)