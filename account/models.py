from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

# Custom User Manager
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email),)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password,)
        user.admin = True
        user.staff = True
        user.save(using=self._db)
        return user


# Custom User model without nickname for auth via email
class MyUser(AbstractBaseUser):

    objects = MyUserManager()

    email = models.EmailField(verbose_name='email address',
                              max_length=255,
                              unique=True,)
    first_name = models.CharField(verbose_name='first name',
                                  max_length=30,
                                  blank=True)
    last_name = models.CharField(verbose_name='last name',
                                 max_length=30,
                                 blank=True)
    active = models.BooleanField(verbose_name='active', default=True)
    admin = models.BooleanField(default=False)  # a superuser
    date_creation = models.DateTimeField(verbose_name='date created', auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active


