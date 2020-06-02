import pytest

from polecat.model.db import S
from polecat.auth import jwt

from polecat_auth.services import register_user


class TestRegisterUser:
    def test_mismatching_passwords(self, db):
        with pytest.raises(Exception, match=r'Passwords don\'t match'):
            register_user('test@test.org', 'a', 'b')

    def test_success_without_selector(self, db):
        result = register_user('test@test.org', 'a', 'a')
        assert result['token'] is not None
        assert result['user'] is not None
        assert result['user'].get('email') is None

    def test_success_with_selector(self, db):
        result = register_user('test@test.org', 'a', 'a', selector=S(user=S('email')))
        assert result['user'] is not None
        assert result['user']['email'] == 'test@test.org'

    def test_upgrade_from_anonymous(self, db, factory):
        anon_user = factory.User(email=None, password=None)
        token = jwt({
            'user_id': anon_user.id,
            'entity_id': anon_user.entity.id,
            'role': 'default'
        })
        result = register_user('test@test.org', 'a', 'a', token=token, selector=S(user=S('email')))
        assert result['user'] is not None
        assert result['user']['id'] == anon_user.id
        assert result['user']['email'] == 'test@test.org'

    def test_upgrade_from_non_anonymous(self, db, factory):
        anon_user = factory.User(email='exists@test.org', password=None)
        token = jwt({
            'user_id': anon_user.id,
            'entity_id': anon_user.entity.id,
            'role': 'default'
        })
        with pytest.raises(Exception, match=r'Cannot register existing user'):
            register_user('test@test.org', 'a', 'a', token=token)
