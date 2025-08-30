# condox/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Em produção use variável de ambiente
SECRET_KEY = "dev-secret-key"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Jazzmin deve vir ANTES do admin
    "jazzmin",

    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party
    "rest_framework",
    "django_filters",

    # apps do projeto
    "accounts.apps.AccountsConfig",
    "condominios",
    "reservas",
    "financeiro",
    "comunicados",
    "galeria",
    "portal",
    "assembleias",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "condox.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # sobrescrever admin/index.html etc.
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "condox.wsgi.application"

# Banco de dados (dev)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Validações de senha
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Localização
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

# Arquivos estáticos e mídia
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # seus CSS/JS do projeto
STATIC_ROOT = BASE_DIR / "staticfiles"    # destino do collectstatic

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"           # uploads

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Usuário custom
AUTH_USER_MODEL = "accounts.User"

# Login/logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# 🎨 Jazzmin (ADMIN claro)
JAZZMIN_SETTINGS = {
    "site_title": "CondoX — Administração",
    "site_header": "CondoX",
    "site_brand": "CondoX",
    "welcome_sign": "Bem-vindo(a) ao painel do CondoX",
    "copyright": "CondoX © 2025",
    "search_model": ["accounts.User", "reservas.Reserva", "financeiro.Lancamento"],
    "show_ui_builder": False,

    # Links no topo
    "topmenu_links": [
        {"name": "Portal", "url": "/", "new_window": False},
        {"app": "reservas"},
        {"app": "financeiro"},
        {"app": "comunicados"},
    ],

    # Ícones das models (sem votações)
    "icons": {
        # Accounts
        "accounts.User": "fas fa-user",
        # Reservas
        "reservas.AreaReservavel": "fas fa-map-pin",
        "reservas.Reserva": "fas fa-calendar-check",
        # Financeiro
        "financeiro.Lancamento": "fas fa-wallet",
        # Comunicados
        "comunicados.Aviso": "fas fa-bullhorn",
        # Condomínios
        "condominios.Condominio": "fas fa-building",
        "condominios.Bloco": "fas fa-cubes",
        "condominios.Unidade": "fas fa-door-closed",
        # Galeria
        "galeria.Evento": "fas fa-camera-retro",
    },

    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "reservas",
        "financeiro",
        "comunicados",
        "condominios",
        "accounts",
    ],

    "changeform_format": "horizontal_tabs",

    # 👉 Tema CLARO
    "theme": "flatly",

    # CSS próprio para ajustes finos do admin
    "custom_css": "css/admin_overrides.css",
}

# Ajustes finos de UI do Jazzmin para tema claro
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-white navbar-light",
    "sidebar": "sidebar-light-primary",
    "accent": "accent-primary",
    "no_navbar_border": False,
    "navbar_small_text": False,
    "sidebar_nav_small_text": False,
    "footer_small_text": True,
}

# Emails aparecem no terminal (modo dev)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# FUTURO POR PELO GMAIL
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "seuemail@gmail.com"
# EMAIL_HOST_PASSWORD = "sua_senha_de_app"  # senha de app, não a senha normal
# DEFAULT_FROM_EMAIL = "CondoX <seuemail@gmail.com>"