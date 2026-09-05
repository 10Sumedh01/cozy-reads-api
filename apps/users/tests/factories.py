import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "TestPass!123")
        if create:
            obj.save()
