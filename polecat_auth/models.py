from polecat import model
from polecat.model import omit

from .policies import OwnerPolicy, OrganisationMemberPolicy, UserPolicy, DirectOrganisationMemberPolicy

__all__ = ('User', 'Organisation', 'JWTType')


class Entity(model.Model):
    """Represents either a user or an organisation. This is useful for
    polymorphic relationships, especially with regard to ownership of
    objects, and RLS.
    """
    pass


class User(model.Model):
    name = model.TextField()
    email = model.EmailField(unique=True)
    password = model.PasswordField(omit=omit.ALL)
    logged_out = model.DatetimeField(omit=omit.ALL)
    created = model.DatetimeField(default=model.Auto)
    anonymous = model.BoolField(default=False)
    entity = model.RelatedField(Entity, related_name='users')  # TODO: One-to-one

    class Meta:
        policies = (
            OwnerPolicy('auth_user.entity'),
        )


class Organisation(model.Model):
    name = model.TextField()
    entity = model.RelatedField(Entity, related_name='organisations')  # TODO: One-to-one

    class Meta:
        policies = (
            DirectOrganisationMemberPolicy(),
        )


class Membership(model.Model):
    user = model.RelatedField(User, null=False, related_name='memberships')
    organisation = model.RelatedField(Organisation, null=False, related_name='memberships')
    role = model.TextField()

    class Meta:
        uniques = (
            ('user', 'organisation', 'role'),
        )
        policies = (
            UserPolicy('auth_membership.user'),
        )


class APIToken(model.Model):
    purpose = model.TextField()


class JWTType(model.Type):
    token = model.TextField()
    user = model.RelatedField(User)  # TODO: Omit reverse relationships
    organisation = model.RelatedField(Organisation)  # TODO: Omit reverse relationships
