from polecat.model.db import S
from polecat.auth import jwt

from polecat_auth.roles import DefaultRole


class TestRegisterMutation:
    def test_success_without_selector(self, server, db):
        result = server.mutation(
            'Register',
            {
                'email': 'test@test.org',
                'password': 'a',
                'password_confirmation': 'a'
            },
            role=DefaultRole.Meta.dbrole
        )
        assert result['token'] is not None

    def test_upgrade_from_anonymous(self, server, db, factory):
        anon_user = factory.User(email=None, password=None)
        token = jwt({
            'user_id': anon_user.id,
            'entity_id': anon_user.entity.id,
            'role': 'default'
        })
        result = server.mutation(
            'Register',
            {
                'email': 'test@test.org',
                'password': 'a',
                'password_confirmation': 'a',
                'token': token
            },
            selector=S(user=S('email')),
            role=DefaultRole.Meta.dbrole
        )
        assert result['token'] is not None
        assert result['user']['id'] == anon_user.id
