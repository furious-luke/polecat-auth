from polecat.auth import jwt
from polecat.admin.command import Command
from polecat.model.db import Q, S

from .models import Entity, User, Organisation, APIToken
from .services import create_user


class CreateUser(Command):
    def get_params(self):
        return (
            self.Argument(('email',)),
            self.Option(('--password',)),
            self.Option(('--name',)),
            self.Option(('--organisation',))
        )

    def run(self, email, password=None, name=None, organisation=None):
        create_user(email, password=password, name=name, organisation=organisation)


class CreateOrganisation(Command):
    def get_params(self):
        return (
            self.Argument(('name',)),
        )

    def run(self, name):
        (
            Q(Organisation)
            .insert(
                name=name,
                entity=Q(Entity).insert().select('id')
            )
            .execute()
        )


class CreateAPIToken(Command):
    def get_params(self):
        return (
            self.Argument(('purpose',)),
            self.Option(('--user-email',)),
            self.Option(('--organisation',))
        )

    def run(self, purpose, user_email=None, organisation=None):
        if not user_email and not organisation:
            # TODO: Better error.
            raise Exception('Must supply one of "user" or "organisation"')
        api_token_id = (
            Q(APIToken)
            .insert(purpose=purpose)
            .select('id')
            .get()
        )['id']
        claims = {
            'api_token_id': api_token_id,
            'role': 'user'
        }
        if user_email:
            results = (
                Q(User)
                .filter(email=user_email)
                .select('id', entity=S('id'))
                .get()
            )
            claims['user_id'] = results['id']
        elif organisation:
            results = (
                Q(Organisation)
                .filter(name=organisation)
                .select('id', entity=S('id'))
                .get()
            )
        if results['entity']['id']:
            claims['entity_id'] = results['entity']['id']
        token = jwt(claims)
        print(f'Claims: {repr(claims)}')
        print(f'API token: {token}')
