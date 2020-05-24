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
