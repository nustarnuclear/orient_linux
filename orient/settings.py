"""
Django settings for orient project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%v($q30)cr5-e)%v9oqjwe-@=b+m!8+*j1vdz2+&rhw_wrd_99'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    #'debug_toolbar',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tragopan',
    'calculation',
    'import_export',
    #'oauth2_provider',
    'rest_framework',
    'rest_framework.authtoken',
    
)

MIDDLEWARE_CLASSES = (
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'orient.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                "django.core.context_processors.i18n",
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]



WSGI_APPLICATION = 'orient.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tragopan',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    
}


#egret setting on centos
USER_HOME_DIR=os.path.expanduser('~django')
DJANGO_WORKSPACE=os.path.join(USER_HOME_DIR,'.django_project')
TMP_DIR=os.path.join(DJANGO_WORKSPACE,'tmp')
EGRET_WORKSPACE=os.path.join(DJANGO_WORKSPACE,'egret_workspace')

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Chongqing'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#open transaction
ATOMIC_REQUESTS=True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS=(os.path.join(BASE_DIR, 'static'),)

#media root
MEDIA_ROOT=os.path.join(DJANGO_WORKSPACE, 'media')
MEDIA_URL="/media/"

#debug tools setting
#DEBUG_TOOLBAR_PATCH_SETTINGS = False
#INTERNAL_IPS=('127.0.0.1','192.168.1.114')

LOGIN_REDIRECT_URL=r'/'
#Custom dashboard
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

#Grappelli setting
GRAPPELLI_ADMIN_TITLE='ORIENT'
GRAPPELLI_SWITCH_USER=True



#django rest framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #]
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGE_SIZE': 10             
}


#django file browser setting

FILEBROWSER_DIRECTORY=''
FILEBROWSER_EXTENSIONS={
    'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
    'Document': ['.pdf','.doc','.rtf','.txt','.xls','.csv','.docx',],
    'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm','.mkv'],
    'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
}
FILEBROWSER_SELECT_FORMATS={
    'file': ['Image','Document','Video','Audio'],
    'image': ['Image'],
    'document': ['Document'],
    'media': ['Video','Audio'],
}
FILEBROWSER_MAX_UPLOAD_SIZE=10000000000
