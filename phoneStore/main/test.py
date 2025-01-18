# from django.core import mail
# from django.test import TestCase


# class EmailTest(TestCase):
#     def test_send_email(self):
#         mail.send_mail(
#             "New form", "Hello",
#             'stepnik0@yandex.ru', ['stepnik0@yandex.ru'],
#         )
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(mail.outbox[0].subject, "New form")
#         self.assertEqual(mail.outbox[0].body, "Hello")