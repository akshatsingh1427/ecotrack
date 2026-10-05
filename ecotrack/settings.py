import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.environ.get('SECRET_KEY','dev-key-change-me')
DEBUG=os.environ.get('DEBUG','1')=='1'
ALLOWED_HOSTS=[h for h in os.environ.get('ALLOWED_HOSTS','*').split(',') if h]
host=os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if host:ALLOWED_HOSTS.append(host)
CSRF_TRUSTED_ORIGINS=[o for o in os.environ.get('CSRF_TRUSTED_ORIGINS','').split(',') if o]
if host:CSRF_TRUSTED_ORIGINS.append('https://'+host)
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
try:
    import whitenoise  # serves static files in production
    MIDDLEWARE.insert(1,'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:pass
ROOT_URLCONF='ecotrack.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','core.ctx.footer']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES['default']=dj_database_url.parse(os.environ['DATABASE_URL'],conn_max_age=600)
STATIC_URL='static/';STATIC_ROOT=BASE_DIR/'staticfiles'
LOGIN_URL='/login/';LOGIN_REDIRECT_URL='/';LOGOUT_REDIRECT_URL='/login/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField';USE_TZ=True;TIME_ZONE='Asia/Kolkata'
if not DEBUG:
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
    SESSION_COOKIE_SECURE=True;CSRF_COOKIE_SECURE=True
