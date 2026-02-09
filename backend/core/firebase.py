import json
import os
import firebase_admin
from firebase_admin import credentials
from django.conf import settings


def get_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred = None
    if settings.FIREBASE_CREDENTIALS and os.path.exists(settings.FIREBASE_CREDENTIALS):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
    elif settings.FIREBASE_CREDENTIALS_JSON:
        cred = credentials.Certificate(json.loads(settings.FIREBASE_CREDENTIALS_JSON))
    else:
        cred = credentials.ApplicationDefault()

    options = {}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    return firebase_admin.initialize_app(cred, options or None)
