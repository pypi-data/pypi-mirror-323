class SharedData:
    def __init__(self):
        self.data = {}

    def set_data(self, identifier, value, destroy=False):
        self.data[identifier] = (value, destroy)

    def get_data(self, identifier):
        value, destroy = self.data.get(identifier, (None, False))
        if destroy:
            self.data.pop(identifier, None)
        return value