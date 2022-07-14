import arango


class ViewProperties():
    '''
    database.create_arangosearch_view(
    name='v_imdb',
    properties={'cleanupIntervalStep': 0}
)
    '''
    def __init__(self):
        self.cleanupIntervalStep=0

        ## Default arango db values
        self.cleanup_interval_step = 0
        self.commit_interval_msec = 1000
        self.consolidation_interval_msec = 0
        # self.consolidation_policy = {
        # type = "tier",
        # segments_min = 1,
        # segments_max = 10,
        # segments_bytes_max = 5368709120,
        # segments_bytes_floor = 2097152,
        # min_score = 0}
        self.primary_sort_compression = "lz4"
        self.writebuffer_idle = 64
        self.writebuffer_active = 0
        self.writebuffer_max_size = 33554432



class View():
    def __init__(self):
        self.name = "sample_view"
        self.view_type = "arangosearch"
        self.properties = ViewProperties()
        self.links = {}


    def __init__(self, name: str, view_type:str,
                 properties: ViewProperties,
                 links: "{}"):
        self.__init__()
        self.name = name
        self.view_type = view_type
        self.links = links
        self.primary_sort = []
        self.stored_values = None # []
        self.properties = properties


    def add_link(self):
        pass

    def create(self, db):
        db.create_view()

