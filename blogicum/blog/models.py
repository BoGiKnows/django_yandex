from django.db import models
from django.contrib.auth import get_user_model

from .constants import CHAR_MAX_LENGTH

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField('Опубликовано', default=True,
                                       help_text='Снимите галочку, '
                                                 'чтобы скрыть публикацию.')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    image = models.ImageField('Фото', blank=True)

    class Meta:
        abstract = True


class Post(BaseModel):
    title = models.CharField('Заголовок', max_length=CHAR_MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.')
    image = models.ImageField('Картинка', upload_to='posts_images', blank=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации',
                               related_name='posts')
    location = models.ForeignKey('Location', on_delete=models.SET_NULL,
                                 null=True, verbose_name='Местоположение')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категория',
                                 related_name='posts')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField('Заголовок', max_length=CHAR_MAX_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры, '
                                      'дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField('Название места', max_length=CHAR_MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
