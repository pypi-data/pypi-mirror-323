from django.db import models
from django.utils.timezone import now


class UnauthorizedAccessAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    attempt_time = models.DateTimeField(default=now)
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100)
    prefer_languages = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Unauthorized Access Attempt"
        verbose_name_plural = "Unauthorized Access Attempts"
        ordering = ['-attempt_time']
        
    
    def __str__(self):
        return f"Attempt from {self.ip_address} at {self.attempt_time}"