from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
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

    def dispatch(self, request, *args, **kwargs):
        self.queryset = Note.objects.filter(owner = request.user)
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
            return super(UpdateView, self).post(request, *args, **kwargs)
        else:
            return redirect(reverse("usernotes-list"))

class NoteDeleteView(DeleteView):
    model = Note
    success_url = "/usernotes/list"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner == request.user:
            return super(DeleteView, self).post(request, *args, **kwargs)
        else:
            return redirect(reverse("usernotes-list"))