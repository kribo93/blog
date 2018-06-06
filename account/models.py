from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from sorl.thumbnail import get_thumbnail
from hitcount.models import HitCount, HitCountMixin
from django.contrib.contenttypes.fields import GenericRelation
from taggit.managers import TaggableManager
from taggit.models import Tag

import re
from django.conf import settings

from django.db.models.signals import post_save

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
        user.is_admin = True
        user.staff = True
        user.save(using=self._db)
        return user


# Custom User model without nickname for auth via email
class User(AbstractBaseUser):

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
    is_admin = models.BooleanField(default=False)  # a superuser
    created_at = models.DateTimeField(verbose_name='date created', auto_now_add=True)

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
        return self.is_admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,
                     self).get_queryset().filter(status='published')

class Post(models.Model, HitCountMixin):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    tags = models.ManyToManyField(Tag)
    slug = models.SlugField(max_length=250, unique_for_date='publish', allow_unicode=True)
    author = models.ForeignKey(User, related_name='blog_posts')
    body = RichTextUploadingField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default='draft')
    objects = models.Manager()
    published = PublishedManager()
    users_like = models.ManyToManyField(User,
                                   related_name='posts_liked',
                                   blank=True)
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation')

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('account:post_detail', args=[self.pk])


class Profile(models.Model):
    nickname = models.CharField(max_length=50,unique=True)
    user = models.OneToOneField(User, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.first_name)

    def get_absolute_url(self):
        return reverse('account:profile', kwargs={'pk': self.pk})

    def get_image_60x60(self):
        return get_thumbnail(self.photo, '60x60', crop='center', quality=50)

class Comment(models.Model):
    post = models.ForeignKey(Post)
    nickname = models.ForeignKey(Profile, on_delete=models.PROTECT)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body

    def get_absolute_url(self):
        return  reverse('account:post_detail', args=[self.post.pk])


