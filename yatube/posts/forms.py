from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post

        fields = ('group', 'text', 'image',)

        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }

        help_texts = {
            'group': 'Выберите группу для новой записи',
            'text': 'Добавьте текст для новой записи'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment

        fields = ('text', )

        help_texts = {
            'text': 'Добавьте комментарий'
        }
