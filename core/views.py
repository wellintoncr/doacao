from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import LoginForm, NameForm, PasswordForm, RegisterForm


class LoginView(auth_views.LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("register_form", RegisterForm())
        return context


class RegisterView(View):
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("event-detail")
        return render(request, "login.html", {"form": LoginForm(request), "register_form": form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return self._render(request, NameForm(instance=request.user), PasswordForm(user=request.user))

    def post(self, request):
        form = NameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Nome atualizado.")
            return redirect("profile")
        return self._render(request, form, PasswordForm(user=request.user))

    def _render(self, request, name_form, password_form):
        return render(request, "profile.html", {"name_form": name_form, "password_form": password_form})


class PasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    form_class = PasswordForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")

    def get(self, request, *args, **kwargs):
        # a troca de senha só existe dentro da página de perfil
        return redirect("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_form"] = context["form"]
        context["name_form"] = NameForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada.")
        return super().form_valid(form)
