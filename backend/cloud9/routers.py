class PaymentRouter:
    """
    Router to control all database operations on payment models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'crypto_payments':
            return 'payment'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'crypto_payments':
            return 'payment'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'crypto_payments' or obj2._meta.app_label == 'crypto_payments':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'crypto_payments':
            return db == 'payment'
        return None

class AnalyticsRouter:
    """
    Router to control all database operations on analytics models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'analytics' or obj2._meta.app_label == 'analytics':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'analytics':
            return db == 'analytics'
        return None
