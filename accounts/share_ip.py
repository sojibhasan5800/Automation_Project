# ------------------------
# Helper: user_or_ip key
# ------------------------
def user_or_ip(group, request):
    """Return user id if logged in, else client IP"""
    if request.user.is_authenticated:
        return str(request.user.pk)
    return request.META.get("REMOTE_ADDR")
