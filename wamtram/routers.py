class WamtramRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'wamtram':
            return 'wamtram'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'wamtram':
            return None
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'wamtram' or obj2._meta.app_label == 'wamtram':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'wamtram':
            return False
        return None
