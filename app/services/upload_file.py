import cloudinary
import cloudinary.uploader
from app.core.config import settings

class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Налаштовуємо Cloudinary при ініціалізації
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантажує файл і повертає посилання (url).
        public_id дозволяє нам перезаписувати аватар, якщо користувач заллє новий.
        """
        r = cloudinary.uploader.upload(
            file.file, 
            public_id=f"CheckApp/{username}", # Папка CheckApp, файл = ім'я юзера
            overwrite=True,
            transformation=[
                {"width": 250, "height": 250, "crop": "fill"}, # Обрізати до квадрата 250px
                {"gravity": "face"} # Центрувати по обличчю (Cloudinary це вміє!)
            ]
        )
        return r["secure_url"]

# Створюємо екземпляр сервісу (можна тут, або через Depends)
upload_service = UploadFileService(
    settings.CLOUDINARY_NAME, 
    settings.CLOUDINARY_API_KEY, 
    settings.CLOUDINARY_API_SECRET
)