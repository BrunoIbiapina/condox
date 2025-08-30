# condox/settings_prod.py
from .settings import *  # importa tudo do base (o seu settings.py atual)
import os, dj_database_url

# Segurança
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY", SECRET_KEY)  # usa a do .env se disponível
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else ["*"]

# Banco via DATABASE_URL (Railway/Render)
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600, 
        ssl_require=True,  # ⚠️ melhor manter True em produção, Railway suporta SSL
        default=os.getenv("DATABASE_URL", "")
    )
}

# Static/Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Garantir whitenoise logo após SecurityMiddleware
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
        "whitenoise.middleware.WhiteNoiseMiddleware"
    )

# Media (uploads) – lembra que Railway é efêmero, ideal usar S3/Cloudflare R2
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email (por enquanto só console, depois trocar por SMTP real)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"