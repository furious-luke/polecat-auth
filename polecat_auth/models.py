from polecat import model
from polecat.model import omit

__all__ = ('User', 'JWTType')


class User(model.Model):
    name = model.TextField()
    email = model.EmailField(unique=True, null=False)
    password = model.PasswordField(omit=omit.ALL)
    created = model.DatetimeField(default=model.Auto)
    logged_out = model.DatetimeField(omit=omit.ALL)


class JWTType(model.Type):
    token = model.TextField()
    user = model.RelatedField(User)  # TODO: Omit reverse relationships
