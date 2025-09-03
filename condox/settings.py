# condox/settings.py
from pathlib import Path
import os

# =========================
# Integração n8n (webhooks)
# =========================
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://brunoibiapina.app.n8n.cloud/webhook-test/da085699-19d2-4fe0-86d1-23f4b3c9d91b",
)
N8N_WEBHOOK_TOKEN = os.getenv("N8N_WEBHOOK_TOKEN", "")

# =========
# Básico
# =========
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# DEBUG: 1/true/True habilita; default True em dev local
DEBUG = os.getenv("DEBUG", "1").lower() in ("1", "true", "yes", "on")

# Hosts permitidos
# Ex.: ALLOWED_HOSTS=condox-production.up.railway.app,localhost,127.0.0.1
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]

# CSRF (precisa do esquema https://)
# Ex.: CSRF_TRUSTED_ORIGINS=https://condox-production.up.railway.app,https://localhost
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "https://localhost,https://127.0.0.1").split(",") if o.strip()
]

INSTALLED_APPS = [
    # Jazzmin antes do admin
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

    # Apps do projeto
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
        "DIRS": [BASE_DIR / "templates"],
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

# ===========================
# Banco de Dados
# - Em dev: SQLite
# - Em Railway: Postgres via envs PG/POSTGRES
# ===========================
if os.getenv("PGHOST") or os.getenv("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", os.getenv("PGDATABASE", "railway")),
            "USER": os.getenv("POSTGRES_USER", os.getenv("PGUSER", "postgres")),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", os.getenv("PGPASSWORD", "")),
            "HOST": os.getenv("PGHOST", "localhost"),
            "PORT": os.getenv("PGPORT", "5432"),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {"sslmode": os.getenv("PGSSLMODE", "require")},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ===========================
# Segurança / Proxy (Railway)
# ===========================
# Faz o Django respeitar X-Forwarded-Proto (https) do proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Cookies seguros em produção
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Opcional endurecimento extra:
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
    # SECURE_SSL_REDIRECT = True

# ===========================
# Validações de senha
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===========================
# Localização
# ===========================
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

# ===========================
# Arquivos estáticos / mídia
# Em produção real, recomendo usar Whitenoise + collectstatic.
# ===========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===========================
# Usuário custom & auth
# ===========================
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ===========================
# Jazzmin (Admin)
# ===========================
JAZZMIN_SETTINGS = {
    "site_title": "CondoX • Administração",
    "site_header": "CondoX",
    "site_brand": "CondoX",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Bem-vindo ao painel administrativo do CondoX",
    "copyright": "CondoX © 2025 • Sistema de Gestão Condominial",
    "search_model": ["accounts.User", "reservas.Reserva", "financeiro.Lancamento"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "🏠 Portal", "url": "/", "new_window": False, "permissions": ["auth.view_user"]},
        {"name": "📊 Dashboard", "url": "/admin/", "new_window": False},
        {"app": "reservas", "name": "📅 Reservas"},
        {"app": "financeiro", "name": "💰 Financeiro"},
        {"app": "comunicados", "name": "📢 Comunicados"},
        {"name": "⚙️ Configurações", "url": "/admin/auth/group/", "new_window": False, "permissions": ["auth.change_group"]},
    ],
    "usermenu_links": [
        {"name": "Dashboard", "url": "/", "icon": "fas fa-tachometer-alt"},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "reservas",
        "financeiro",
        "comunicados",
        "condominios",
        "galeria",
        "assembleias",
        "accounts",
        "auth",
    ],
    "icons": {
        "accounts.User": "fas fa-user-circle",
        "auth.User": "fas fa-users",
        "auth.Group": "fas fa-users-cog",
        "reservas.AreaReservavel": "fas fa-map-marked-alt",
        "reservas.Reserva": "fas fa-calendar-check",
        "financeiro.Lancamento": "fas fa-file-invoice-dollar",
        "comunicados.Aviso": "fas fa-bullhorn",
        "condominios.Condominio": "fas fa-building",
        "condominios.Bloco": "fas fa-cubes",
        "condominios.Unidade": "fas fa-door-open",
        "galeria.Evento": "fas fa-images",
        "assembleias.Assembleia": "fas fa-gavel",
        "assembleias.Pauta": "fas fa-list-check",
        "votacoes.Pauta": "fas fa-vote-yea",
        "votacoes.Voto": "fas fa-hand-paper",
    },
    "related_modal_active": False,
    "custom_css": "css/admin_premium.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "list_filter_horizontal": True,
    "language_chooser": False,
}
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar_small_text": False,
    "footer_small_text": True,
    "sidebar_nav_small_text": False,
    "sidebar_nav_flat_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_compact_style": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "theme": "lux",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": False,
}

# ===========================
# Email
# ===========================
# Em dev:
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Futuro (Gmail):
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "seuemail@gmail.com"
# EMAIL_HOST_PASSWORD = "sua_senha_de_app"
# DEFAULT_FROM_EMAIL = "CondoX <seuemail@gmail.com>"