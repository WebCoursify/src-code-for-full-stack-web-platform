from django.db import models


class UserManager(models.Manager):
    def find_by_id(self, id):
        result = self.filter(id=id, deleted=0)
        if result.exists():
            return result[0]
        else:
            return None

class User(models.Model):
    ROLE_ADMIN  = 1
    ROLE_AUTHOR = 2

    objects  = UserManager()
    username = models.CharField(max_length=50)
    email    = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    description = models.CharField(max_length=512, null=True)
    role     = models.SmallIntegerField()

    avatar   = models.CharField(max_length=512, null=True)
    follows  = models.ManyToManyField('User')
    deleted  = models.BooleanField(default=0)

    @property
    def article_number(self):
        return len(Article.objects.filter(author_id=self.id, deleted=0))

    @property
    def following_count(self):
        return len(self.follows.all())

    @property
    def follower_count(self):
        return len(self.user_set.all())

    def get_followers(self):
        return self.user_set.all()

    def get_followings(self):
        return self.follows.all()

    def add_following(self, user_to_follow):
        self.follows.add(user_to_follow)

    def remove_following(self, user_to_cancel_follow):
        self.follows.remove(user_to_cancel_follow)

    def is_following(self, user):
        if self.follows.filter(id=user.id).exists():
            return True
        else:
            return False

    """


    def get_followers(self):
        return User.objects.raw('''select u.id,username,email,password,description,role,deleted from
                                app_user u inner join app_userfollowuser re
                                on u.id=re.follower_id and re.following_id=%d
                                where re.followed=1''' % self.id)

    def get_followings(self):
        return User.objects.raw('''select u.id,username,email,password,description,role,deleted from app_user u
                                inner join app_userfollowuser re
                                on u.id=re.following_id and re.follower_id=%d
                                where re.followed=1''' % self.id)

    def add_following(self, user_to_follow):
        relation = UserFollowUser.objects.raw('''select * from app_userfollowuser re
                                               where re.follower_id=%d and re.following_id=%d'''
                                               % (self.id, user_to_follow.id))
        if len(list(relation)) > 0:
            relation = relation[0]
            if relation.followed == 1:
                return
            relation.followed = 1
            relation.save()
        else:
            UserFollowUser.objects.create(follower_id=self.id, following_id=user_to_follow.id)


    def remove_following(self, user_to_cancel_follow):
        relation = UserFollowUser.objects.raw('''select * from app_userfollowuser re
                                               where re.follower_id=%d and re.following_id=%d'''
                                               % (self.id, user_to_cancel_follow.id))
        if len(list(relation)) > 0:
            relation = relation[0]
            if relation.followed == 0:
                return
            relation.followed = 0
            relation.save()
    """


class ArticleQuerySet(models.query.QuerySet):
    def published(self):
        return self.filter(state=Article.STATE_PUBLISHED)

    def drafts(self):
        return self.filter(state=Article.STATE_UNPUBLISHED)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model)

    def search(self, query=None, sort=None, page=None, count=None, published=None):
        """
        :param query:
        :param sort:
        :param page:
        :param count:
        :param published:
        :return: tuple, query result and total count
        """
        if query:
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

        total_count = result_set.count()

        if count is not None:
            if page is None:
                result_set = result_set[: count]
            else:
                result_set = result_set[page * count: (page + 1) * count]

        return total_count, result_set


class Article(models.Model):
    STATE_UNPUBLISHED = 1
    STATE_PUBLISHED   = 2

    objects  = ArticleManager()
    author   = models.ForeignKey('User', related_name='author')

    title    = models.CharField(max_length=100)
    content  = models.TextField()
    time_create = models.DateTimeField()
    time_update = models.DateTimeField(auto_now=True)
    state    = models.SmallIntegerField()
    deleted  = models.BooleanField(default=0)
    liked_user = models.ManyToManyField(User)

    @property
    def like_num(self):
        return len(self.liked_user.all())
    @property
    def comments(self):
        return ArticleComment.objects.filter(article_id=self.id).order_by('-time')

    def add_like_user(self, user):
        self.liked_user.add(user)

    def remove_like_user(self, user):
        self.liked_user.remove(user)

    def does_user_like(self, user):
        return self.liked_user.filter(id=user.id).exists()


class UserFollowUser(models.Model):
    follower = models.ForeignKey('User', related_name='follower')
    following = models.ForeignKey('User', related_name='following')
    followed = models.BooleanField(default=1)


class ArticleComment(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(User)
    content = models.TextField()
    time = models.DateTimeField()







