from polecat import model
from polecat.auth import jwt
from polecat.model.db import Q

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
            Q(User)
            .filter(email=email, password=password)
            .select('id')
            .get()
        )
        return {
            'token': jwt({'userId': result['id']})
        }
