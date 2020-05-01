#  импортируем Generic View, чтобы создать ему наследника
from django.views.generic import CreateView

#  функция reverse_lazy позволяет получить URL по параметру "name" функции path()
from django.urls import reverse_lazy

#  импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


from django.core.mail import send_mail


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login") #  где login — это параметр "name" в path()
    template_name = "signup.html"
    

send_mail(
        'Тема письма',
        'Текст письма.',
        'from@example.com',  # Это поле От:
        ['to@example.com'],  # Это поле Кому:
        fail_silently=False, # сообщать об ошибках
)
