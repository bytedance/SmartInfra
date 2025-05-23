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
from distutils.command.config import config
from email.policy import default

from decouple import config
import os.path
from pathlib import Path
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c+ozv-7yx^#y_0fcj0v+g2v#^jzi0c$+iit_cpys4+r#*g6xkx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'salt',
    'ansible',
    'django_q',

]

# Django-Q configuration
Q_CLUSTER = {
    'name': 'SmartInfra',
    'workers': 8,
    'recycle': 500,
    'timeout': 172800,
    'retry': 173000,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 50,
    'label': 'Django Q',
    'max_attempts': 3,
    'orm': 'default',  # 使用 Django ORM 作为后端
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 设置Session的有效时间（单位为秒）：
SESSION_COOKIE_AGE = 1800

# 设置Session在浏览器关闭时失效
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 启用Session的过期时间刷新
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = 'smartinfra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "salt/templates"), os.path.join(BASE_DIR, "ansible/templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartinfra.wsgi.application'

# FTP 配置
SFTP_STORAGE_ROOT = config('TRANSFER_FILE_HOME')
SFTP_STORAGE_INTERACTIVE = False

# DB 配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "DEFAULT_CHARSET": "utf8mb4",
        "NAME": config('DB_NAME', default='smartinfra'),
        "USER": config('DB_USER', default='root'),
        "PASSWORD": config('DB_PASSWORD', default='123456'),
        "HOST": config('DB_HOST', default='127.0.0.1'),
        "PORT": config('DB_PORT', default=3306),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "salt/static")]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'

# LOG配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s]- %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/smartinfra.log",
            "maxBytes": 1024 * 1024 * 100,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "django-q": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/qcluster.log",
            "maxBytes": 1024 * 1024 * 100,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "default": {  # default日志
            "handlers": ["console", "default"],
            "level": "INFO",
        },
        "django-q": {  # django_q模块相关日志
            "handlers": ["console", "django-q"],
            "level": "INFO",
            "propagate": False,
        },

    },
}

# 定时刷新minion时间间隔, 以分钟为单位计算. 同时定义时区，防止重复执行. 支持 'UTC', 'Asia/Shanghai', 与数据库时区匹配
FRESH_INTERVAL = config('FRESH_INTERVAL', default=60)
FRESH_TIMEZONE = config('FRESH_TIMEZONE', default='Asia/Shanghai')

# 文件下载目录
DOWNLOAD_URL = config('DOWNLOAD_URL', default='download/')
DOWNLOAD_ROOT = os.path.join(BASE_DIR, DOWNLOAD_URL)

# state根目录
STATE_HOME = config('STATE_HOME', default='smartinfra_state/')

# 上传文件大小
UPLOAD_FILE_SIZE=config('UPLOAD_FILE_SIZE', default=3)

