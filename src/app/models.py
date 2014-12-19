from django.db import models


class User(models.Model):
    ROLE_ADMIN  = 1
    ROLE_AUTHOR = 2

    username = models.CharField(max_length=50)
    email    = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    description = models.CharField(max_length=512, null=True)
    role     = models.SmallIntegerField()
    deleted  = models.BooleanField(default=0)


class Article(models.Model):
    STATE_UNPUBLISHED = 1
    STATE_PUBLISHED   = 2

    author   = models.ForeignKey('User')
    title    = models.CharField(max_length=100)
    content  = models.TextField()
    time_create = models.DateTimeField()
    time_update = models.DateTimeField(auto_now=True)
    state    = models.SmallIntegerField()
    deleted  = models.BooleanField(default=0)


##########################
# TODO: User Follow User #
##########################



###########################
# TODO: User Like Article #
###########################



#######################
# TODO: User Comments #
#######################










