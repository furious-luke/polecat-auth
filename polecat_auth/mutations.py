from polecat import model
from polecat.auth import jwt, jwt_decode
from polecat.model.db import Q, S

from .exceptions import AuthError
from .models import JWTType, User, Entity
from .services import register_user

__all__ = ('AuthenticateInput', 'Authenticate', 'RefreshAnonymousUser')


class AuthenticateInput(model.Type):
    email = model.EmailField()
    password = model.PasswordField()

    class Meta:
        input = True


class Authenticate(model.Mutation):
    input = AuthenticateInput
    returns = JWTType

    def resolve(self, ctx):
        input = ctx.parse_input()
        email = input['email']
        password = input['password']
        result = (
            Q(User)
            .filter(email=email, password=password)
        )
        selector = S('id', entity=S('id'))
        selector.merge(ctx.selector.get('user'))
        result = result.select(selector).get()
        if not result:
            raise AuthError('Invalid email/password')
        return {
            'token': jwt({
                'user_id': result['id'],
                'entity_id': result['entity']['id'],
                'role': 'user'
            }),
            'user': result
        }


class RefreshAnonymousUserInput(model.Type):
    token = model.TextField()

    class Meta:
        input = True


class RefreshAnonymousUser(model.Mutation):
    input = RefreshAnonymousUserInput
    returns = JWTType

    def resolve(self, ctx):
        input = ctx.parse_input()
        try:
            token = input['token']
            claims = jwt_decode(token)
            query = Q(User).filter(id=claims['user_id'])
            # TODO: This is a little inefficient, but is needed to
            # confirm the user actually exists.
            if query.select('id').get() is None:
                raise Exception
        except Exception:
            # TODO: Check more.
            # TODO: These should be composable, but the nested select
            # from Polecat doesn't seem to be working as expected.
            entity_id = Q(Entity).insert().select('id').get()['id']
            query = (
                Q(User)
                .insert(
                    entity=entity_id,
                    anonymous=True
                )
            )
            token = None
        if ctx.selector and 'user' in ctx.selector.lookups:
            query = query.select(S(entity=S('id')).merge(ctx.selector.lookups.get('user')))
        user = query.get()
        if not token:
            token = jwt({
                'user_id': user['id'],
                'entity_id': (user['entity'] or {}).get('id'),
                'role': 'default'
            })
        return {
            'token': token,
            'user': user
        }


class RegisterInput(model.Type):
    email = model.EmailField()
    password = model.PasswordField()
    password_confirmation = model.PasswordField()
    token = model.TextField()

    class Meta:
        input = True


class Register(model.Mutation):
    input = RegisterInput
    returns = JWTType

    def resolve(self, ctx):
        input = ctx.parse_input()
        email = input['email']
        password = input['password']
        password_confirmation = input['password_confirmation']
        token = input.get('token')
        return register_user(email, password, password_confirmation, token=token, selector=ctx.selector)
