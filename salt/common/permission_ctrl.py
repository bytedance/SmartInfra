# -*- coding: UTF-8 -*-

import logging
from django.http import HttpResponseForbidden
from functools import wraps

logger = logging.getLogger("default")

def superuser_required(func):
    @wraps(func)
    def _wrapped_view(request):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page")
        return func(request)
    return _wrapped_view