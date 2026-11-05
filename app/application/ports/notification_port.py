from abc import ABC, abstractmethod

from app.application.dtos.notification_message import NotificationMessage

class NotificationPort(ABC):

    @abstractmethod
    def send_notification(self, notification: NotificationMessage) -> None:
        pass