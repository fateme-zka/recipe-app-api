import uuid
import os

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)
from django.conf import settings  # this is a recommended way to retrieve different settings from the django settings


def recipe_image_file_path(instance, filename):
    """Generate file path for the new recipe image that was uploaded"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and Saves a new user"""

        if not email or not password:
            raise ValueError("Users must have an email address and password.")

        # normalized_email() is helpful function that comes with BaseUserManager
        # docs: Normalizes email addresses by lower-casing the domain portion of the email address.
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and Save a new superuser"""
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # by default username field name is "username" but we are customizing to email
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for the recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.IntegerField()
    link = models.CharField(max_length=255, blank=True)  # link of the recipe if it's stored online
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    # we don't put () at the end of the function because we just want to reference to this function
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
