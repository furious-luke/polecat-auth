from polecat import model

__all__ = ('User', 'JWTType')


class User(model.Model):
    name = model.TextField()
    email = model.EmailField(unique=True, null=False)
    password = model.PasswordField()
    created = model.DatetimeField(default=model.Auto)
    logged_out = model.DatetimeField()


class JWTType(model.Type):
    token = model.TextField()
    user = model.RelatedField(User)  # TODO: Omit reverse relationships
