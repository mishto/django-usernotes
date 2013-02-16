from string import split
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, ProcessFormView, ModelFormMixin, FormMixin, BaseUpdateView, DeleteView
from django.views.generic.list import ListView
from usernotes.models import Note
from django.shortcuts import redirect


def owner_is_user_required(function):
    def _decorator(request, *args, **kwargs):
        if int(request.POST["owner"]) == request.user.id:
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse("usernotes-list"))
    return _decorator

class NoteListView(ListView):
    model = Note

    def dispatch(self, request, *args, **kwargs):
        self.queryset = Note.objects.filter(published = True)
        return super(ListView, self).dispatch(request, *args, **kwargs)

class NoteListUserView(ListView):
    model = Note

    def get_queryset(self):
        queryset = Note.objects.filter(owner = self.kwargs["user_id"])
        if int(self.kwargs["user_id"]) != self.request.user.id:
            queryset = queryset.filter(published = True)
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super(ListView, self).dispatch(request, *args, **kwargs)

class NoteCreateView(CreateView):
    model = Note

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    @method_decorator(owner_is_user_required)
    def post(self, request, *args, **kwargs):
        return super(CreateView, self).post(request, *args, **kwargs)

class NoteDetailView(DetailView):
    model = Note

class NoteUpdateView(UpdateView):
    model = Note

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    @method_decorator(owner_is_user_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner == request.user :
            return ProcessFormView.post(self, request, *args, **kwargs)
        else:
            return HttpResponseForbidden(self)

class NoteDeleteView(DeleteView):
    model = Note
    success_url = "/usernotes/list"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        if object.owner == request.user:
            object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseForbidden(self)

class NotePublishView(UpdateView):
    model = Note

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner == request.user:
            self.object.published = True
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseForbidden(self)

class NoteUnpublishView(UpdateView):
    model = Note

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner == request.user:
            self.object.published = False
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseForbidden(self)

class NoteSearchView(ListView):
    model = Note

    def get_queryset(self):
        keywords = split(self.request.GET["keywords"], " ")
        queryset = Note.objects.filter(published=True)
        for key in keywords:
            queryset = queryset.filter(
                Q(text__icontains=key)
                | Q(title__icontains=key))
        return queryset