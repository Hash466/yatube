from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': '* Выберите группу из списка',
            'text': '* Поле с текстом поста обязательно для заполнения',
            'image': '* Выберите картинку для добавления к посту'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': '* Поле для текста вашего комментария',
        }
