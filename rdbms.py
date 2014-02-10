from google.appengine.api import rdbms

class Connection(object):
    def __init__(self, instance, db=None):
        self.instance = instance
        self.db = db
        self.connection = None

    def __enter__(self):
        self.connection = rdbms.connect(self.instance, self.db)
        return self.connection

    def __exit__(self, ext_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()

        self.connection.close()
