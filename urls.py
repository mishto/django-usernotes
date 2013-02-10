from django.conf.urls import url, patterns
from usernotes.views import NoteListView, NoteDetailView, NoteCreateView, NoteUpdateView

urlpatterns = patterns('',
                url(r'^list/$', NoteListView.as_view(), name='usernotes-list'),
                url(r'^create/$', NoteCreateView.as_view(), name='usernotes-create'),
                url(r'^detail/(?P<pk>[\d]+)$', NoteDetailView.as_view(), name='usernotes-detail'),
                url(r'^edit/(?P<pk>[\d]+)$', NoteUpdateView.as_view(), name='usernotes-update'),
            )

