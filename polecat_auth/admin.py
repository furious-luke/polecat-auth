from polecat.admin.command import Command
from polecat.model.db import Q

from .models import User


class CreateUser(Command):
    def get_params(self):
        return (
            self.Argument(('email',)),
            self.Argument(('password',)),
            self.Option(('--name',))
        )

    def run(self, email, password, name=None):
        (
            Q(User)
            .insert(email=email, password=password, name=name)
            .execute()
        )
