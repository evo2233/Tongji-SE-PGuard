from tortoise.models import Model
from tortoise import fields

class User(Model):
    userId = fields.UUIDField(pk=True)
    userName = fields.TextField(unique=True)
    password = fields.TextField()
    location = fields.TextField()
    sumCount = fields.SmallIntField()