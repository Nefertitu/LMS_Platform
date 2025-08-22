from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    """Тест-кейс для проверки CRUD представлений модели 'Lesson'"""

    def setUp(self) -> None:
        """Инициализация тестовых данных"""

        self.user = User.objects.create(email="testuser@example.com")
        self.course = Course.objects.create(
            course_title="Test course", description="Test", owner=self.user, price=10000.00
        )
        self.lesson = Lesson.objects.create(title="Test lesson", course=self.course, owner=self.user, price=1000.00)
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self) -> None:
        """Тест получения деталей урока"""

        url = reverse("materials:lesson-detail", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)

    def test_lesson_create(self) -> None:
        """Тест создания нового урока"""

        url = reverse("materials:lesson-create")
        data = {"title": "Python", "course": self.course.pk, "price": 2000.00}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self) -> None:
        """Тест обновления деталей урока"""

        url = reverse("materials:lesson-update", args=(self.lesson.pk,))
        data = {
            "title": "Python",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Python")

    def test_lesson_delete(self) -> None:
        """Тест удаления урока"""

        url = reverse("materials:lesson-delete", args=(self.lesson.pk,))
        data = {
            "title": "Python",
        }
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)
        self.assertEqual(data.get("title"), "Python")

    def test_lesson_list(self) -> None:
        """Тест списка уроков"""

        url = reverse("materials:lesson-list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lesson.objects.all().count(), 1)
        self.assertEqual(len(data["results"]), 1)
        lesson_data = data["results"][0]
        self.assertEqual(lesson_data["id"], self.lesson.pk)
        self.assertEqual(lesson_data["title"], self.lesson.title)
        self.assertEqual(lesson_data["price"], "1000.00")
        self.assertEqual(lesson_data["course_title"], self.lesson.course.course_title)

    def test_lesson_create_invalid_link(self) -> None:
        """Тест создания нового урока с невалидной ссылкой"""

        url = reverse("materials:lesson-create")
        invalid_data = {
            "title": "Урок с неверной ссылкой",
            "link": "https://rutube.ru/lesson/2/",
            "course": self.course.pk,
            "price": 1100.00,
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(response.data["non_field_errors"][0], "Материалы должны быть размещены на YouTube")


class CourseTestCase(APITestCase):
    """Тест-кейс для проверки CRUD представлений модели 'Course'"""

    def setUp(self) -> None:
        """Инициализация тестовых данных"""

        self.user = User.objects.create(email="testuser@example.com")
        self.course = Course.objects.create(
            course_title="Test course", description="Test", owner=self.user, price=10000.00
        )
        self.lesson = Lesson.objects.create(title="Test lesson", course=self.course, owner=self.user, price=2100.00)
        # self.subscriber = User.objects.create(email="subscriber@example.com")
        # self.subscription = Subscription.objects.create(user=self.subscriber, course=self.course, is_active=True)
        self.client.force_authenticate(user=self.user)
        # self.client.force_authenticate(user=self.subscriber)

    def test_course_retrieve(self) -> None:
        """Тест получения деталей курса"""

        url = reverse("materials:courses-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("course_title"), self.course.course_title)
        self.assertEqual(data.get("price"), "10000.00")

    #
    def test_course_create(self) -> None:
        """Тест создания нового курса"""

        url = reverse("materials:courses-list")
        data = {"course_title": "Test course", "lesson": self.lesson.pk, "price": 11000.00}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_update(self) -> None:
        """Тест обновления деталей курса"""

        url = reverse("materials:courses-detail", args=(self.course.pk,))
        data = {
            "course_title": "Kotlin",
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("course_title"), "Kotlin")

    def test_course_delete(self) -> None:
        """Тест удаления курса"""

        url = reverse("materials:courses-detail", args=(self.course.pk,))
        data = {
            "course_title": "Kotlin",
        }
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)
        self.assertEqual(data.get("course_title"), "Kotlin")

    def test_course_list(self) -> None:
        """Тест списка курсов"""

        url = reverse("materials:courses-list")
        response = self.client.get(url)
        data = response.json()
        print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lesson.objects.all().count(), 1)
        self.assertEqual(len(data["results"]), 1)
        course_data = data["results"][0]
        self.assertEqual(course_data["id"], self.course.pk)
        self.assertEqual(course_data["course_title"], self.course.course_title)
        self.assertEqual(course_data["price"], "10000.00")
        self.assertEqual(course_data["lessons"][0], self.lesson.title)
        self.assertEqual(course_data["lessons_count"], Lesson.objects.all().count())


class SubscriptionTestCase(APITestCase):
    """Тест-кейс для проверки представлений модели 'Subscription'"""

    def setUp(self) -> None:
        """Инициализация тестовых данных"""

        self.user = User.objects.create(email="testuser@example.com")
        self.course = Course.objects.create(
            course_title="Test course", description="Test", owner=self.user, price=10000.00
        )
        self.subscriber = User.objects.create(email="subscriber@example.com")
        self.client.force_authenticate(user=self.subscriber)

    def test_add_subscription(self) -> None:
        """Проверка создания новой подписки"""
        url = reverse("materials:subscriptions")
        response = self.client.post(
            url,
            {
                "course": self.course.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.subscriber,
                course=self.course,
                is_active=True,
            ).exists()
        )
        self.assertIn(response.data["message"], ["Подписка добавлена"])

    #
    def test_remove_subscription(self) -> None:
        """Проверка отмены существующей подписки"""

        Subscription.objects.create(user=self.subscriber, course=self.course, is_active=True)

        url = reverse("materials:subscriptions")
        response = self.client.post(url, {"course": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.subscriber, course=self.course, is_active=True).exists()
        )

    def test_subscription_list(self) -> None:
        """Тест списка подписок"""

        subscription = Subscription.objects.create(user=self.subscriber, course=self.course, is_active=True)

        url = reverse("materials:subscriptions-list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.all().count(), 1)
        self.assertEqual(len(data["results"]), 1)
        subscription_data = data["results"][0]
        self.assertEqual(subscription_data["id"], subscription.pk)
        self.assertEqual(subscription_data["user_email"], self.subscriber.email)
        self.assertEqual(subscription_data["course_title"], self.course.course_title)
        self.assertTrue(subscription_data["is_active"])
