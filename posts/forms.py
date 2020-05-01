from django.forms import ModelForm

from posts.models import Post, Comment

# cоздание класса формы
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
