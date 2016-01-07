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


class ArticleQuerySet(models.query.QuerySet):
    def published(self):
        return self.filter(state=Article.STATE_PUBLISHED)

    def drafts(self):
        return self.filter(state=Article.STATE_UNPUBLISHED)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model)

    def search(self, query=None, sort=None, page=None, count=None, published=None):
        if query is not None:
            result_set = self.filter(title__icontains=query, deleted=0)
        else:
            result_set = self.filter(deleted=0)

        if published is not None:
            if published:
                result_set = result_set.published()
            else:
                result_set = result_set.drafts()

        if sort is not None:
            result_set = result_set.order_by(sort)

        if count is not None:
            if page is None:
                result_set = result_set[: count]
            else:
                result_set = result_set[page * count: (page + 1) * count]

        return result_set


class Article(models.Model):
    STATE_UNPUBLISHED = 1
    STATE_PUBLISHED   = 2

    objects  = ArticleManager()
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










