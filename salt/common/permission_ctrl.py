# -*- coding: UTF-8 -*-
"""
This is the MIT license: http://www.opensource.org/licenses/mit-license.php

Copyright (c) 2017 by Konstantin Lebedev.

Copyright 2022- 2023 Bytedance Ltd. and/or its affiliates

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import traceback

from django.http import HttpResponseForbidden
from functools import wraps
from salt.models import shell_template

logger = logging.getLogger("default")

def superuser_required(func):
    @wraps(func)
    def _wrapped_view(request):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You have no permission to access this page")
        return func(request)
    return _wrapped_view

def st_access_required(func):
    @wraps(func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if shell_template.objects.get(id=kwargs.get("id", None)).user != request.user:
                return HttpResponseForbidden("You have no permission to access this template")
        except Exception as e:
            logger.error(traceback.format_exc())
            return HttpResponseForbidden("You have no permission to access this template")
        return func(request, *args, **kwargs)
    return _wrapped_view