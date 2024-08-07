class DB_route:
    """
    A router to control all database operations on models in the application.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'handles_data':
            return 'handles_db'
        if model._meta.app_label == 'pid_data':
            return 'pid_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'handles_data':
            return 'handles_db'
        if model._meta.app_label == 'pid_data':
            return 'pid_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'handles_data' or \
           obj2._meta.app_label == 'pid_data':
           return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'handles_data' or \
            app_label == 'pid_data':
            return None
        return 'default'