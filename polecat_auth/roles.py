from polecat import model

__all__ = ('AdminRole', 'UserRole', 'DefaultRole')


class AdminRole(model.Role):
    pass


class UserRole(model.Role):
    parents = (AdminRole,)


class DefaultRole(model.Role):
    parents = (UserRole,)
