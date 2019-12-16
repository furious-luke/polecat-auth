from polecat.model import session
from polecat.db.sql.expression.where import Where


class IsOwnerOrMemberResolver:
    def __init__(self, column_name):
        self.column_name = column_name

    def build_query(self, context, *args, **kwargs):
        query = context(*args, **kwargs)
        entity_id = session('claim.entity_id', 'int')
        expr = Where(**{f'{self.column_name}__organisations__memberships__user__entity': entity_id})
        expr.merge(Where(**{self.column_name: entity_id}), boolean='OR')
        query = query.filter(expr)
        import pdb; pdb.set_trace()
        print(list(query))
        return query
