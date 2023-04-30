from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm
from yatube.settings import TEST_FORM_URL

User = get_user_model()


class PostsFormsTests(TestCase):
    """Тестирование формы поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.form = PostForm()
        cls.user = User.objects.create_user(
            username='forms_user'
        )
        cls.group = Group.objects.create(
            title='Заголовок формы',
            slug='forms_group',
            description='Описание формы',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Текст формы',
        )
        cls.group_check = Group.objects.create(
            title='Тестирование формы',
            slug='forms_slug',
            description='Формы, повсюду формы',
        )
        cls.form_data = {
            'group': cls.group.id,
            'text': cls.post.text,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Тестирование создания новой записи."""
        count_posts = Post.objects.count()
        context = {
            'group': self.group.id,
            'text': 'Какой-то текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=context,
            follow=True
        )
        self.assertEqual(
            Post.objects.latest('id').text, context['text']
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user])
        )
        self.assertEqual(
            Post.objects.count(), count_posts + 1
        )
        self.assertTrue(
            Post.objects.filter(
                group=context['group'],
                text=context['text'],
            ).exists()
        )
        print('test forms: Новые записи успешно создаются.')

    def test_editing_post(self):
        """Тестирование редактирования записи."""
        count_posts = Post.objects.count()
        context = {
            'group': self.group_check.id,
            'text': 'Какой-то текст',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=context,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(
            Post.objects.count(), count_posts
        )
        self.assertTrue(Post.objects.filter(
            id=self.post.id, text=context['text'],
            group=context['group']).exists()
        )
        print('test forms: Записи успешно редактируются.')

    def test_anonim_client_create_post(self):
        """Тестирование возможности создания записи без
        регистрации.
        """
        post = Post.objects.count()

        response = self.client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post)
        self.assertRedirects(response, TEST_FORM_URL)

        print('test forms: Записи без логина не создаются.')

    def test_edit_other_person_post(self):
        """Тестирование невозможности редактировать чужие записи."""
        user = User.objects.create(
            username='forms_some_other_user'
        )
        auth_other_user = Client()
        auth_other_user.force_login(user)

        form_data = {
            'group': self.group.id,
            'text': 'Какой-то текст',
        }

        response = auth_other_user.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=form_data,
            follow=True
        )

        post = Post.objects.get(id=self.post.pk)
        form_fields = [
            [post.group, self.post.group],
            [post.author, self.post.author],
            [post.text, self.post.text],
        ]

        for field, attribute in form_fields:
            self.assertEqual(field, attribute)

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[self.post.id])
        )
        print('test forms: Чужие записи не редактируются.')

    def test_post_help_text(self):
        """Coverage-зависимость. Тестирование text_field и
        group_field.
        """
        response = PostsFormsTests.post
        fields_help_texts = {
            'group': 'Выберите группу для новой записи',
            'text': 'Добавьте текст для новой записи',
        }

        for field, fields in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    response._meta.get_field(field).help_text, fields
                )
        print('test forms: Формы text_field и group_field работают.')
