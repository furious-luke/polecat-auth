from polecat.model.db import Q, S
from polecat.db.connection import transaction
from polecat.auth import jwt, jwt_decode

from .models import Entity, User, Organisation, Membership


def register_user(email, password, password_confirmation, token=None, selector=None):
    if password != password_confirmation:
        raise Exception('Passwords don\'t match')
    selector = selector or S()
    if token:
        claims = jwt_decode(token)
        try:
            user = Q(User).filter(id=claims['user_id']).select('id', 'email').get()
            if user['email']:
                raise Exception('Cannot register existing user')
        except (KeyError, AttributeError):
            raise Exception('Invalid token for user registration')
        user = upgrade_user(
            user['id'],
            email,
            password,
            selector=(selector.get('user') or S()).merge(S(entity=S('id')))
        )
    else:
        user = create_user(
            email,
            password=password,
            selector=(selector.get('user') or S()).merge(S(entity=S('id')))
        )
    token = jwt({
        'user_id': user['id'],
        'entity_id': user['entity']['id'],
        'role': 'default'
    })
    return {
        'token': token,
        'user': user
    }


def create_user(email, password=None, name=None, organisation=None, selector=None):
    with transaction():
        # TODO: These should be composable, but the nested select
        # from Polecat doesn't seem to be working as expected.
        entity_id = Q(Entity).insert().select('id').get()['id']
        user = (
            Q(User)
            .insert(
                email=email,
                password=password,
                name=name,
                entity=entity_id
            )
            .select(S('id').merge(selector))
            .get()
        )
        user_id = user['id']
        if organisation is not None:
            org = (
                Q(Organisation)
                .insert_if_missing({'name': organisation})
                .select('id', 'entity')
                .get()
            )
            if not org['entity']:
                (
                    Q(Organisation)
                    .filter(id=org['id'])
                    .update(entity=Q(Entity).insert())
                    .execute()
                )
            # TODO: Update "active" to be a query against other actives.
            (
                Q(Membership)
                .insert(
                    user=user_id,
                    organisation=org['id'],
                    active=True
                )
                .execute()
            )
        return user


def upgrade_user(user_id, email, password, selector=None):
    user = (
        Q(User)
        .filter(id=user_id)
        .update(
            email=email,
            password=password
        )
        .select(S('id').merge(selector))
        .get()
    )
    return user
