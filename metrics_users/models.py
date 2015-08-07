from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class SmallsUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'

    class Meta(AbstractBaseUser.Meta):
        db_table = 'users_smallsuser'
        managed=False
