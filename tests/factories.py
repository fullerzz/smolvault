from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from smolvault.auth.models import NewUserDTO


class UserFactory(ModelFactory[NewUserDTO]):
    username = Use(lambda: ModelFactory.__faker__.user_name())
    email = Use(lambda: ModelFactory.__faker__.email())
    full_name = Use(lambda: ModelFactory.__faker__.name())
    password = Use(lambda: ModelFactory.__faker__.password())
