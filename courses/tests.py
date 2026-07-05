from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Course, Category, Module, Lesson, Enrollment

User = get_user_model()

class LessonAccessTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            category=self.category,
            instructor='Test Instructor',
            price=0.0,
            is_free=True
        )
        self.module = Module.objects.create(course=self.course, title='Test Module', order=1)
        
        # Create a preview lesson
        self.preview_lesson = Lesson.objects.create(
            module=self.module,
            title='Preview Lesson',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            duration='10:00',
            order=1,
            is_preview=True,
            is_published=True
        )
        
        # Create a locked lesson
        self.locked_lesson = Lesson.objects.create(
            module=self.module,
            title='Locked Lesson',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            duration='10:00',
            order=2,
            is_preview=False,
            is_published=True
        )

    def test_anonymous_user_can_access_preview_lesson(self):
        response = self.client.get(reverse('courses:lesson_player', args=[self.preview_lesson.id]))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_for_locked_lesson(self):
        response = self.client.get(reverse('courses:lesson_player', args=[self.locked_lesson.id]))
        self.assertEqual(response.status_code, 302)
        expected_url = f"{reverse('courses:detail', args=[self.course.id])}?locked=1"
        self.assertRedirects(response, expected_url)

    def test_enrolled_user_can_access_locked_lesson(self):
        # Enroll user
        Enrollment.objects.create(user=self.user, course=self.course, is_active=True)
        self.client.login(username='testuser', password='password')
        
        response = self.client.get(reverse('courses:lesson_player', args=[self.locked_lesson.id]))
        self.assertEqual(response.status_code, 200)

    def test_unenrolled_authenticated_user_is_redirected_for_locked_lesson(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('courses:lesson_player', args=[self.locked_lesson.id]))
        self.assertEqual(response.status_code, 302)
        expected_url = f"{reverse('courses:detail', args=[self.course.id])}?locked=1"
        self.assertRedirects(response, expected_url)
