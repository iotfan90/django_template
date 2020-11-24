from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.http import is_safe_url
from django.shortcuts import render, redirect
from api.forms import UserLoginForm


def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')


def login_user(request):
    """
    Login a user
    """
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    form = UserLoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if is_safe_url(redirect_path, request.get_host()):
                        return redirect(redirect_path)

                    return redirect('home')
                else:
                    messages.error(
                        request, "Inactive Account. Please Contact Admin Support")
                    return HttpResponseRedirect(request.path_info)

            else:
                messages.error(request, "Invalid login credentials")
                return HttpResponseRedirect(request.path_info)

    context = {
        "form": form,
    }
    return render(request, 'login.html', context)


def home(request):
    if request.user.is_authenticated:
        user = request.user
        context = {
            "user": user
        }
        return render(request, 'home.html', context)
    else:
        return redirect('login')


def repeat_play2_outcome(request):
    if request.user.is_authenticated:
        user = request.user
        context = {
            "user": user
        }
        return render(request, 'repeat_play_2_outcome.html', context)
    else:
        return redirect('login')

