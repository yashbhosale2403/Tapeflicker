import os
import mimetypes
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import firebase_admin
from firebase_admin import storage

@deconstructible
class FirebaseMediaStorage(Storage):
    def __init__(self, **kwargs):
        # Ensure Firebase is initialized (calls config/firebase.py setup)
        import config.firebase
        from django.conf import settings
        bucket_name = getattr(settings, 'FIREBASE_STORAGE_BUCKET', None)
        if bucket_name:
            self.bucket = storage.bucket(bucket_name)
        else:
            self.bucket = storage.bucket()

    def _clean_name(self, name):
        """Standardize separators to forward slashes for storage bucket paths"""
        return name.replace('\\', '/')

    def _open(self, name, mode='rb'):
        clean_name = self._clean_name(name)
        blob = self.bucket.blob(clean_name)
        from io import BytesIO
        from django.core.files.base import ContentFile
        data = blob.download_as_bytes()
        return ContentFile(data, name=clean_name)

    def _save(self, name, content):
        clean_name = self._clean_name(name)
        blob = self.bucket.blob(clean_name)
        
        # Guess the MIME type to ensure files open correctly in the browser
        content_type, _ = mimetypes.guess_type(clean_name)
        if not content_type:
            content_type = 'application/octet-stream'
            
        content.seek(0)
        blob.upload_from_file(content, content_type=content_type)
        
        # Make the uploaded object public
        try:
            blob.make_public()
        except Exception as e:
            # Fallback if Uniform Bucket-Level Access or IAM permissions prevent ACL modifications
            pass
            
        return clean_name

    def exists(self, name):
        clean_name = self._clean_name(name)
        blob = self.bucket.blob(clean_name)
        return blob.exists()

    def url(self, name):
        clean_name = self._clean_name(name)
        # Construct/retrieve the public URL from the Firebase storage bucket
        blob = self.bucket.blob(clean_name)
        return blob.public_url

    def delete(self, name):
        clean_name = self._clean_name(name)
        blob = self.bucket.blob(clean_name)
        if blob.exists():
            blob.delete()
