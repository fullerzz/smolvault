import logging
from datetime import datetime, timedelta

from smolvault.clients.database import DatabaseClient
from smolvault.config import get_settings

logger = logging.getLogger(__name__)


class UploadValidator:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.daily_upload_limit_bytes = self.settings.daily_upload_limit_bytes
        self.whitelist = self.settings.user_whitelist.split(",")

    def upload_allowed(self, user_id: int, db_client: DatabaseClient) -> bool:
        valid = self._uploads_under_limit_prev_24h(user_id, db_client) and self._user_on_whitelist(user_id)
        logger.info("Upload allowed result for user %s: %s", user_id, valid)
        return valid

    def _uploads_under_limit_prev_24h(self, user_id: int, db_client: DatabaseClient) -> bool:
        logger.info("Checking upload limit for user %s", user_id)
        start_time = datetime.now() - timedelta(days=1)
        metadata = db_client.get_all_metadata(user_id, start_time=start_time)
        bytes_uploaded = sum([record.size for record in metadata])
        logger.info(
            "User %s has uploaded %d bytes in the last 24 hours. DAILY_LIMIT: %d",
            user_id,
            bytes_uploaded,
            self.daily_upload_limit_bytes,
        )
        return bytes_uploaded < self.daily_upload_limit_bytes

    def _user_on_whitelist(self, user_id: int) -> bool:
        logger.info("Checking whitelist for user %s", user_id)
        return str(user_id) in self.whitelist


class UserCreationValidator:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.users_limit = self.settings.users_limit

    def user_creation_allowed(self, db_client: DatabaseClient) -> bool:
        users: int = db_client.get_user_count()
        logger.info("%d users currently in the system", users)
        return users < self.users_limit
