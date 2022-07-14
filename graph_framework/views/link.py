class Link():
    '''
     link = {
      "includeAllFields": True,
      "fields" : { "description" : { "analyzers" : [ "text_en" ] } }
    }

    '''


    class Field():
        def __init__(self):
            self.field_name = "field_name"
            self.analyzers = ["text_en"]

    def __init__(self):
        self.includeAllFields = True
        self.name = "link_name"
        self.fields = []
        self.analyzers = ["identity"]

    def add_field(self, field):
        self.fields.append(field)

    def __get__(self):
        return vars(self)
