from polecat.db.schema.policy import Policy


class OrganisationMemberPolicy(Policy):
    def __init__(self, column_name):
        expr = (
            'EXISTS ('
            ' SELECT 1 FROM auth_user usr'
            ' INNER JOIN auth_membership mem ON mem.user = usr.id'
            ' INNER JOIN auth_organisation org ON org.id = mem.organisation'
            " WHERE usr.entity = current_setting('claims.entity_id', TRUE)::int"
            ' AND {} = mem.organisation'
            ')'
        ).format(column_name)
        super().__init__(column_name, expr)


class DirectOrganisationMemberPolicy(Policy):
    def __init__(self):
        column_name = 'auth_organisation.id'
        expr = (
            'EXISTS ('
            ' SELECT 1 FROM auth_membership mem'
            " WHERE mem.user = current_setting('claims.user_id', TRUE)::int"
            ' AND mem.organisation = {}'
            ')'
        ).format(column_name)
        super().__init__(column_name, expr)


class OwnerPolicy(Policy):
    def __init__(self, column_name):
        expr = (
            "{} = current_setting('claims.entity_id', TRUE)::int"
        ).format(column_name)
        super().__init__(column_name, expr)


class UserPolicy(Policy):
    def __init__(self, column_name):
        expr = (
            "{} = current_setting('claims.user_id', TRUE)::int"
        ).format(column_name)
        super().__init__(column_name, expr)
