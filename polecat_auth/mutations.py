from polecat import model
from polecat.auth import jwt
from polecat.model.db import Q

from .exceptions import AuthError
from .models import JWTType, User

__all__ = ('AuthenticateInput', 'Authenticate')


class AuthenticateInput(model.Type):
    email = model.EmailField()
    password = model.PasswordField()

    class Meta:
        input = True


class Authenticate(model.Mutation):
    input = AuthenticateInput
    returns = JWTType

    def resolve(self, email, password):
        result = (
            Q(User, session=self.session)
            .filter(email=email, password=password)
        )
        if self.selector and 'user' in self.selector.lookups:
            result = result.select(self.selector.lookups.get('user'))
        result = result.get()
        if not result:
            raise AuthError('Invalid email/password')
        return {
            'token': jwt({'user_id': result['id']}),
            'user': result
        }
