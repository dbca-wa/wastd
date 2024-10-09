class Wamtram2Router:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "wamtram2":
            return "wamtram2"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "wamtram2":
            return "wamtram2"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._state.db == obj2._state.db:
            return True
        if obj1._meta.app_label == "wamtram2" or obj2._meta.app_label == "wamtram2":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == "wamtram2":
            False
        return None
