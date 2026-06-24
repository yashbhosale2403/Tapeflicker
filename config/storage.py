import os
import logging
import urllib.request
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

@deconstructible
class CloudinaryMediaStorage(Storage):
    def __init__(self, **kwargs):
        from django.conf import settings
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    def _clean_name(self, name):
        """Standardize separators to forward slashes for Cloudinary paths"""
        return name.replace('\\', '/')

    def _open(self, name, mode='rb'):
        clean_name = self._clean_name(name)
        url = self.url(clean_name)
        try:
            logger.info(f"CloudinaryMediaStorage: Downloading {clean_name} from {url}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                return ContentFile(response.read(), name=clean_name)
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage ERROR: Failed to open/download {clean_name}: {e}", exc_info=True)
            raise e

    def _save(self, name, content):
        clean_name = self._clean_name(name)
        # Cloudinary expects public_id WITHOUT extension (it adds it dynamically)
        public_id, _ = os.path.splitext(clean_name)
        
        content.seek(0)
        try:
            logger.info(f"CloudinaryMediaStorage: Uploading {clean_name} as public_id {public_id}...")
            cloudinary.uploader.upload(
                content,
                public_id=public_id,
                unique_filename=False,
                overwrite=True,
                resource_type="auto"
            )
            logger.info(f"CloudinaryMediaStorage: Successfully uploaded {clean_name} to Cloudinary.")
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage ERROR: Failed to upload {clean_name} to Cloudinary: {e}", exc_info=True)
            raise e
            
        return clean_name

    def exists(self, name):
        clean_name = self._clean_name(name)
        url = self.url(clean_name)
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req) as resp:
                return resp.status == 200
        except Exception:
            return False

    def url(self, name):
        clean_name = self._clean_name(name)
        # Generate the secure URL using Cloudinary SDK
        url, _ = cloudinary.utils.cloudinary_url(clean_name, secure=True)
        return url

    def delete(self, name):
        clean_name = self._clean_name(name)
        public_id, _ = os.path.splitext(clean_name)
        try:
            logger.info(f"CloudinaryMediaStorage: Deleting public_id {public_id} from Cloudinary...")
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage ERROR: Failed to delete {clean_name}: {e}", exc_info=True)
