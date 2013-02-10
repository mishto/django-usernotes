from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

class Note(models.Model):
    owner = models.ForeignKey(User)
    title = models.TextField()
    text = models.TextField()

    def get_absolute_url(self):
        return reverse('usernotes-detail', kwargs={'pk': self.pk})