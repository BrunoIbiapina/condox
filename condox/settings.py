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

# 🎨 Jazzmin (ADMIN moderno)
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
    
    # Top navigation
    "topmenu_links": [
        {"name": "🏠 Portal", "url": "/", "new_window": False, "permissions": ["auth.view_user"]},
        {"name": "📊 Dashboard", "url": "/admin/", "new_window": False},
        {"app": "reservas", "name": "📅 Reservas"},
        {"app": "financeiro", "name": "💰 Financeiro"},
        {"app": "comunicados", "name": "📢 Comunicados"},
        {"name": "⚙️ Configurações", "url": "/admin/auth/group/", "new_window": False, "permissions": ["auth.change_group"]},
    ],

    # User menu on the top right
    "usermenu_links": [
        {"name": "Dashboard", "url": "/", "icon": "fas fa-tachometer-alt"},
        {"model": "auth.user"}
    ],

    # Side navigation
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

    # Icons for models - Ícones modernos e consistentes
    "icons": {
        # Accounts & Auth
        "accounts.User": "fas fa-user-circle",
        "auth.User": "fas fa-users",
        "auth.Group": "fas fa-users-cog",
        
        # Reservas - Ícones relacionados a agendamento
        "reservas.AreaReservavel": "fas fa-map-marked-alt",
        "reservas.Reserva": "fas fa-calendar-check",
        
        # Financeiro - Ícones relacionados a dinheiro
        "financeiro.Lancamento": "fas fa-file-invoice-dollar",
        
        # Comunicados - Ícones de comunicação
        "comunicados.Aviso": "fas fa-bullhorn",
        
        # Condomínios - Ícones relacionados a estrutura
        "condominios.Condominio": "fas fa-building",
        "condominios.Bloco": "fas fa-cubes",
        "condominios.Unidade": "fas fa-door-open",
        
        # Galeria - Ícones relacionados a eventos
        "galeria.Evento": "fas fa-images",
        
        # Assembleias - Ícones relacionados a reuniões
        "assembleias.Assembleia": "fas fa-gavel",
        "assembleias.Pauta": "fas fa-list-check",
        
        # Votações - Ícones relacionados a votação
        "votacoes.Pauta": "fas fa-vote-yea",
        "votacoes.Voto": "fas fa-hand-paper",
    },

    # Related modal behavior
    "related_modal_active": False,

    # Custom CSS & JS
    "custom_css": "css/admin_premium.css",
    "custom_js": None,
    
    # Use modals instead of popups
    "use_google_fonts_cdn": True,
    
    # Show the UI customizer on the sidebar
    "show_ui_builder": False,

    # Change form format
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
    # List per page options
    "list_filter_horizontal": True,
    
    # Add language chooser to top menu
    "language_chooser": False,
}

# Ajustes finos de UI do Jazzmin - Tema moderno e elegante
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
    "theme": "lux",  # Tema Bootstrap elegante
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary", 
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
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