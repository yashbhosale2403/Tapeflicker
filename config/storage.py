import os
import logging
import urllib.request
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

_cloudinary_configured = False

def _configure_cloudinary():
    global _cloudinary_configured
    if not _cloudinary_configured:
        from django.conf import settings
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        _cloudinary_configured = True

@deconstructible
class CloudinaryMediaStorage(Storage):
    """
    Custom Django Storage backend that stores all media uploads on Cloudinary.
    Firebase Authentication is NOT affected — this class is used only for
    ImageField/FileField uploads (course thumbnails, banners, event banners, etc.).
    """

    def __init__(self, **kwargs):
        _configure_cloudinary()

    def _clean_name(self, name):
        """Standardize separators to forward slashes for Cloudinary paths."""
        return name.replace('\\', '/')

    def _public_id(self, name):
        """
        Returns the Cloudinary public_id for a given file name.
        Cloudinary public_ids do NOT include the file extension for images.
        E.g. 'course_thumbnails/abc123.jpg' → 'course_thumbnails/abc123'
        """
        clean = self._clean_name(name)
        root, _ = os.path.splitext(clean)
        return root

    def _open(self, name, mode='rb'):
        _configure_cloudinary()
        clean_name = self._clean_name(name)
        url = self.url(clean_name)
        try:
            logger.info(f"CloudinaryMediaStorage: Downloading {clean_name} from {url}...")
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                return ContentFile(response.read(), name=clean_name)
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage: Failed to open {clean_name}: {e}", exc_info=True)
            raise

    def _save(self, name, content):
        _configure_cloudinary()
        clean_name = self._clean_name(name)
        public_id = self._public_id(clean_name)

        content.seek(0)
        try:
            logger.info(f"CloudinaryMediaStorage: Uploading as public_id='{public_id}'...")
            result = cloudinary.uploader.upload(
                content,
                public_id=public_id,
                unique_filename=False,
                overwrite=True,
                resource_type="auto",
            )
            logger.info(f"CloudinaryMediaStorage: Upload OK → {result.get('secure_url')}")
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage: Upload FAILED for '{clean_name}': {e}", exc_info=True)
            raise

        # Return the original name so Django stores the relative path in the DB.
        return clean_name

    def exists(self, name):
        """
        Check if a resource exists on Cloudinary.
        Uses the Admin API for an authoritative check.
        Returns False on any error (e.g. if credentials aren't set yet locally).
        """
        _configure_cloudinary()
        public_id = self._public_id(name)
        try:
            cloudinary.api.resource(public_id)
            return True
        except cloudinary.api.NotFound:
            return False
        except Exception:
            return False

    def url(self, name):
        """
        Returns the secure Cloudinary HTTPS URL for the stored file.
        Django templates call {{ course.thumbnail.url }} which calls this method.
        """
        _configure_cloudinary()
        public_id = self._public_id(name)
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            secure=True,
            resource_type="image",
        )
        return url

    def delete(self, name):
        _configure_cloudinary()
        public_id = self._public_id(name)
        try:
            logger.info(f"CloudinaryMediaStorage: Deleting public_id='{public_id}'...")
            cloudinary.uploader.destroy(public_id, resource_type="image")
        except Exception as e:
            logger.error(f"CloudinaryMediaStorage: Delete FAILED for '{public_id}': {e}", exc_info=True)
