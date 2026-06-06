from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')(view_func)

def hr_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.profile.role == 'hr'), login_url='login')(view_func)

def admin_or_hr_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.profile.role in ['admin', 'hr']), login_url='login')(view_func)
