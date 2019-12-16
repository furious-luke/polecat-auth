from polecat import model
from polecat.auth import jwt, jwt_decode
from polecat.model.db import Q, S

from .exceptions import AuthError
from .models import JWTType, User

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
        except Exception:
            # TODO: Check more.
            query = Q(User).insert(anonymous=True)
            token = None
        if ctx.selector and 'user' in ctx.selector.lookups:
            query = query.select(ctx.selector.lookups.get('user'), entity=S('id'))
        user = query.get()
        if not token:
            token = jwt({
                'user_id': user['id'],
                'entity_id': user['entity']['id'],
                'role': 'default'
            })
        return {
            'token': token,
            'user': user
        }
