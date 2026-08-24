class NodeAdapters:
    """Host adapter library loaded by cli_host; this module has no executable entry."""

    def __init__(self, storage, http):
        self.storage = storage
        self.http = http
