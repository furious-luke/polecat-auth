import pytest

from polecat.model.db import S

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
        result = register_user('test@test.org', 'a', 'a', S(user=S('email')))
        assert result['user'] is not None
        assert result['user']['email'] == 'test@test.org'
