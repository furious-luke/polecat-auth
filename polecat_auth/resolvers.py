from polecat.model import session
from polecat.model.db import Q, S
from polecat.db.sql.expression.where import Where

from .models import Membership


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


class ActiveOrganisationEntityResolver:
    def __init__(self, column_name='owner'):
        self.column_name = column_name

    def build_model(self, context, **kwargs):
        model = context(**kwargs)
        user_id = context.session.variables.get('claims.user_id')
        # TODO: Improve this query with better filtering.
        entity_id = (
            Q(Membership)
            .filter(active=True, user=user_id)
            .select(organisation=S(entity=S('id')))
            .get()
        )
        try:
            entity_id = entity_id['organisation']['entity']['id']
        except (KeyError, TypeError):
            entity_id = None
        setattr(model, self.column_name, entity_id)
        return model
