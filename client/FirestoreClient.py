import firebase_admin
from firebase_admin import firestore, credentials
import os
# Application Default credentials are automatically created.
cred = credentials.Certificate('servooKey.json')

#cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_firestore_client():
    return db
