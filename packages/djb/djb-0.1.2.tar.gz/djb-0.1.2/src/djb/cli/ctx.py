class DjbContext:
    def __init__(self):
        # djb options.
        self.project = None
        self.debug = False
        self.verbose = False


class DjbInstallContext(DjbContext):
    def __init__(self):
        super().__init__()

        # djb install options.
        self.update = False
