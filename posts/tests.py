from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client

from users.forms import User
from .models import Post, Group, Follow, Comment


class ProfileTest(TestCase):

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
        self.user_two = User.objects.create_user(username="dj", email="dj.s@skynet.com", password="123456")
        self.client.login(username="sarah", password="12345")
        self.group = Group.objects.create(title="group_name", slug="sgroup", description="tests group from sarah")
        self.post = Post.objects.create(author=self.user, text="TEXT", group=self.group)

    def test_profile(self):
        response = self.client.get(f"/{self.user.username}/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.login(username="sarah", password="12345")

        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/new/", {"text": "tests_posting"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(text="tests_posting", author=self.user).exists())
    
    def test_non_auth_user_creates_new_post(self):
        self.client.logout()

        response = self.client.get("/new/")
        self.assertRedirects(response, "/auth/login/?next=/new/")
       
    def test_new_post_in_all_page(self):
        self.client.login(username="sarah", password="12345")

        response = self.client.get("/")
        self.assertContains(response, self.post.text, status_code=200)

        response = self.client.get(f"/{self.user.username}/")
        self.assertContains(response, self.post.text, status_code=200)

        response = self.client.get(f"/{self.user.username}/{self.post.id}/")
        self.assertContains(response, self.post.text, status_code=200)
                
    def test_edit_post_in_all_page(self):
        text = "You are talking about things!"
        edit_post = "You are do not talking about things!"
        self.client.login(username="sarah", password="12345")
        post = Post.objects.create(text=text, author=self.user)

        response = self.client.post(f"/{self.user.username}/{post.id}/edit/", {"text": edit_post}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, edit_post, status_code=200)

        response = self.client.get(f"/{self.user.username}/")
        self.assertContains(response, edit_post, status_code=200)

        response = self.client.get(f"/{self.user.username}/{post.id}/")
        self.assertContains(response, edit_post, status_code=200)
    
    def test_error404(self):
        response = self.client.get("/lsd/")
        self.assertEqual(response.status_code, 404)
    
    def test_post_with_img(self):
        self.client.login(username="sarah", password="12345")

        with open("./posts/test_files/file.jpg", "rb") as img: 
            self.client.post("/new/", {"text": "text", "group": self.group.id,  "image": img})
        
        response = self.client.get("/")
        self.assertContains(response, "<img", status_code=200)

        response = self.client.get(f"/{self.user.username}/")
        self.assertContains(response, "<img", status_code=200)

        response = self.client.get(f"/{self.user.username}/2/")
        self.assertContains(response, "<img")

        response = self.client.get(f"/group/{self.group.slug}/")
        self.assertContains(response, "<img")
        
    def test_notimage_on_pages(self):
        self.client.login(username="sarah", password="12345")

        post = Post.objects.create(author=self.user, text="text")
        with open("./posts/test_files/runserver.txt", "rb") as img:
            post_notimage = self.client.post(f"/{self.user.username}/{post.id}/edit/", {'author': self.user, 'text': 'text', 'image': img}, follow=True)
        
        response = self.client.get(f"/{self.user.username}/{post.id}/edit/")
        self.assertNotContains(response, "<img", status_code=200)
        
    def test_cash_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        key = make_template_fragment_key("index_page")
        cashe = cache.get(key)
        self.assertFalse(cashe is None)

    def test_following(self):
        self.client.login(username="dj", password="123456")

        response = self.client.get("/sarah/follow/")
        self.assertRedirects(response, "/follow/")

        newpost = Post.objects.create(author=self.user, text="TEXT")
        response = self.client.get("/follow/")
        self.assertContains(response, newpost.text)
        self.assertTrue(Follow.objects.filter(user=self.user_two, author=self.user).exists())
        
    def test_unfollowing(self):
        self.client.login(username="dj", password="123456") 

        response = self.client.get("/sarah/unfollow/")
        self.assertRedirects(response, "/sarah/")

        newpost = Post.objects.create(author=self.user, text="TEXT")
        response = self.client.get("/follow/")
        self.assertNotContains(response, newpost.text)
        self.assertFalse(Follow.objects.filter(user=self.user_two, author=self.user).exists())
        
    def test_not_cooment(self):
        self.client.logout()

        response = self.client.get(f"/{self.user.username}/{self.post.id}/comment")
        self.assertRedirects(response, f"/auth/login/?next=/{self.user.username}/{self.post.id}/comment", status_code=302, target_status_code=200)

    def test_comment(self):
        self.client.login(username="dj", password="123456")

        response = self.client.post(f"/{self.user.username}/{self.post.id}/comment",
                                    {"text": "my_comment"}, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/{self.user.username}/{self.post.id}/")
        self.assertContains(response, "my_comment")   
