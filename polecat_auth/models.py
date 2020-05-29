from polecat import model
from polecat.model import omit

from .policies import OwnerPolicy, OrganisationMemberPolicy, UserPolicy, DirectOrganisationMemberPolicy

__all__ = ('User', 'Organisation', 'JWTType')


class Entity(model.Model):
    """Represents either a user or an organisation. This is useful for
    polymorphic relationships, especially with regard to ownership of
    objects, and RLS.
    """
    class Meta:
        plural = 'Entities'


class User(model.Model):
    name = model.TextField(null=True)
    email = model.EmailField(null=True, unique=True)
    password = model.PasswordField(null=True, omit=omit.ALL)
    logged_out = model.DatetimeField(null=True, omit=omit.ALL)
    created = model.DatetimeField(default=model.Auto)
    anonymous = model.BoolField(default=False)
    entity = model.RelatedField(Entity, related_name='users', null=True)  # TODO: One-to-one

    class Meta:
        policies = (
            OwnerPolicy('auth_user.entity'),
        )


class Organisation(model.Model):
    name = model.TextField()
    entity = model.RelatedField(Entity, related_name='organisations', null=True)  # TODO: One-to-one

    class Meta:
        policies = (
            DirectOrganisationMemberPolicy(),
        )


class Membership(model.Model):
    user = model.RelatedField(User, related_name='memberships')
    organisation = model.RelatedField(Organisation, related_name='memberships')
    role = model.TextField(null=True)
    active = model.BoolField(default=False)

    class Meta:
        # TODO: How to unique only one active per user? Check?
        uniques = (
            ('user', 'organisation', 'role'),
        )
        policies = (
            UserPolicy('auth_membership.user'),
        )


class APIToken(model.Model):
    purpose = model.TextField(null=True)


class JWTType(model.Type):
    token = model.TextField()
    user = model.RelatedField(User, null=True)  # TODO: Omit reverse relationships
    organisation = model.RelatedField(Organisation, null=True)  # TODO: Omit reverse relationships
