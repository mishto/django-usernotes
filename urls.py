from django.conf.urls import url, patterns
from usernotes.views import NoteListView, NoteDetailView, NoteCreateView, NoteUpdateView, NoteSearchView
from usernotes.views import NoteDeleteView, NoteListUserView, NotePublishView, NoteUnpublishView

urlpatterns = patterns('',
                url(r'^list/$', NoteListView.as_view(), name='usernotes-list'),
                url(r'^list-user/(?P<user_id>[\d]+)$', NoteListUserView.as_view(), name='usernotes-list-user'),
                url(r'^create/$', NoteCreateView.as_view(), name='usernotes-create'),
                url(r'^detail/(?P<pk>[\d]+)$', NoteDetailView.as_view(), name='usernotes-detail'),
                url(r'^edit/(?P<pk>[\d]+)$', NoteUpdateView.as_view(), name='usernotes-update'),
                url(r'^delete/(?P<pk>[\d]+)$', NoteDeleteView.as_view(), name='usernotes-delete'),
                url(r'^publish/(?P<pk>[\d]+)$', NotePublishView.as_view(), name='usernotes-publish'),
                url(r'^unpublish/(?P<pk>[\d]+)$', NoteUnpublishView.as_view(), name='usernotes-unpublish'),
                url(r'^search/$', NoteSearchView.as_view(), name='usernotes-search'),
            )

