# -*- coding: UTF-8 -*-
"""
// Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
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
            if shell_template.objects.get(id=kwargs.get("id", None)).user != request.user and not request.user.is_superuser:
                return HttpResponseForbidden("You have no permission to access this template")
        except Exception as e:
            logger.error(traceback.format_exc())
            return HttpResponseForbidden("You have no permission to access this template")
        return func(request, *args, **kwargs)
    return _wrapped_view