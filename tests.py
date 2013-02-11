from unittest import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.testcases import TransactionTestCase
from usernotes.models import Note

class TestNotesViews(TransactionTestCase):
    def setUp(self):
        self.c = Client()
        self.basicNoteData = {"owner":0, "title": "basic note title", "text": "basic note text", "published": True}
        self.newNoteData = {"owner":0, "title": "new note title", "text": "new note text", "published": True}
        self.userData = {"username": "username", "email": "email@test.com", "password": "password"}

    def testResponseOKWhenNoNotes(self):
        response = self.c.get(reverse("usernotes-list"))
        self.assertEqual(response.status_code, 200)

    def testListsANote(self):
        self.createNote(self.createUser())
        response = self.c.get(reverse("usernotes-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("note title", response.content)

    def testNoteCreate(self):
        user = self.login()
        self.basicNoteData["owner"] = user.id
        self.c.post(reverse("usernotes-create"), data = self.basicNoteData)
        counter = Note.objects.count()
        self.assertEqual(counter, 1)

    def testNoteDetail(self):
        note = self.createNote(self.createUser())
        response = self.c.get(reverse("usernotes-detail", kwargs={"pk": note.id}))
        self.assertIn("note text", response.content)

    def testNoteUpdate(self):
        user = self.login()
        note = self.createNote(user)
        self.newNoteData["owner"] = user.id
        self.newNoteData["pk"] = note.id
        response = self.c.post(reverse("usernotes-update", kwargs = {"pk": note.id}), data = self.newNoteData)

        self.assertRedirects(response, reverse("usernotes-detail", kwargs={"pk": note.id}))
        note = Note.objects.get(id = note.id)
        self.assertEqual(note.text, self.newNoteData["text"])

    def testCannotCreateNoteIfNotLoggedIn(self):
        user = self.createUser()
        self.basicNoteData["owner"] = user.id
        self.c.post(reverse("usernotes-create"), data = self.basicNoteData)
        notesCount = Note.objects.count()
        self.assertEqual(notesCount, 0)

    def testCannotUpdateNoteIfNotLoggedIn(self):
        user = self.createUser()
        note = self.createNote(user)
        self.newNoteData["owner"] = user.id
        self.c.post(reverse("usernotes-update", kwargs={"pk": note.id}), data = self.newNoteData)
        note = Note.objects.get(id = note.id)
        self.assertEqual(note.text, self.basicNoteData["text"])


    def testCannotUpdateNoteOwner(self):
        user = self.login()
        note = self.createNote(user)
        other_user = self.createUser(username="other")
        self.newNoteData["owner"] = other_user.id
        self.newNoteData["pk"] = note.id
        self.c.post(reverse("usernotes-update", kwargs = {"pk": note.id}), data = self.newNoteData)

        note = Note.objects.get(id = note.id)
        self.assertEqual(note.owner.id, user.id)
        self.assertEqual(note.text, self.basicNoteData["text"])

    def testCannotCreateNoteForOtherUser(self):
        self.login()
        other_user = self.createUser(username = "other")
        self.basicNoteData["owner"] = other_user.id
        self.c.post(reverse("usernotes-create"), data = self.basicNoteData)

        counter = Note.objects.count()
        self.assertEqual(counter, 0)

    def testCannotUpdateNoteOfDifferentUser(self):
        self.login()
        other_user = self.createUser(username="other")
        note = self.createNote(other_user)
        self.newNoteData["owner"] = other_user.id
        self.c.post(reverse("usernotes-update", kwargs = {'pk': note.id}), data=self.newNoteData)

        note = Note.objects.get(id = note.id)
        self.assertEqual(note.text, self.basicNoteData["text"])

    def testCanDeleteNote(self):
        user = self.login()
        note = self.createNote(user)
        self.c.post(reverse("usernotes-delete", kwargs={'pk': note.id}))
        count = Note.objects.count()
        self.assertEqual(count, 0)

    def testCannotDeleteNoteIfNotLoggedIn(self):
        note = self.createNote(self.createUser())
        self.c.post(reverse("usernotes-delete", kwargs={'pk': note.id}))
        count = Note.objects.count()
        self.assertEqual(count, 1)

    def testCannotDeleteSomebodyElseSNote(self):
        other = self.createUser(username="other_user")
        note = self.createNote(other)
        self.login()
        self.c.post(reverse("usernotes-delete", kwargs={'pk': note.id}))
        count = Note.objects.count()
        self.assertEqual(count, 1)

    def testListUserNotesDoesNotDisplayOtherUsersNotes(self):
        user = self.createUser()
        note = self.createNote(user)
        other_user = self.createUser(username = "other_user")
        self.newNoteData["owner"] = other_user
        other_note = self.createNoteWithData(data = self.newNoteData)

        response = self.c.get(reverse("usernotes-list-user", kwargs={'user_id': user.id}))
        self.assertIn(note.title, response.content)
        self.assertNotIn(other_note.title, response.content)

    def testListNotesDoesNotDisplayUnpublishedNotes(self):
        user = self.createUser()
        self.basicNoteData["owner"] = user
        self.basicNoteData["published"] = False
        note = self.createNoteWithData(self.basicNoteData)

        response = self.c.get(reverse("usernotes-list"))
        self.assertNotIn(note.title, response.content)

    def testListUserNotesDisplaysUnpublishedNotesWhenOwnerIsLoggedIn(self):
        user = self.login()
        self.basicNoteData["owner"] = user
        self.basicNoteData["published"] = True
        unpublished_note = self.createNoteWithData(self.basicNoteData)

        self.newNoteData["owner"] = user
        self.newNoteData["published"] = True
        published_note = self.createNoteWithData(self.newNoteData)

        response = self.c.get(reverse("usernotes-list-user", kwargs={'user_id': user.id}))
        self.assertIn(unpublished_note.title, response.content)
        self.assertIn(published_note.title, response.content)

    def testListUserNotesDoesntDisplaysUnpublishedNotesWhenOwnerIsNotLoggedIn(self):
        self.login()
        user = self.createUser(username="other_user")
        self.basicNoteData["owner"] = user
        self.basicNoteData["published"] = False
        unpublished_note = self.createNoteWithData(self.basicNoteData)

        self.newNoteData["owner"] = user
        self.newNoteData["published"] = True
        published_note = self.createNoteWithData(self.newNoteData)

        response = self.c.get(reverse("usernotes-list-user", kwargs={'user_id': user.id}))
        self.assertNotIn(unpublished_note.title, response.content)
        self.assertIn(published_note.title, response.content)

    def createUser(self, username="username", email = "email@test.com", password="password"):
        return User.objects.create_user(username = username, email = email, password = password)

    def login(self, user = None):
        if not user:
            user = self.createUser()
        self.c.login(username=self.userData["username"], password=self.userData["password"])
        return user

    def createNote(self, user):
        self.basicNoteData["owner"] = user
        note = Note.objects.create(**self.basicNoteData)
        return note

    def createNoteWithData(self, data=None):
        note = Note.objects.create(**data)
        return note



