from tortoise.models import Model
from tortoise import fields
import uuid

class User(Model):
    userId = fields.UUIDField(pk=True, default=uuid.uuid4)
    userName = fields.CharField(max_length=40, unique=True)
    password = fields.CharField(max_length=100)
    location = fields.CharField(max_length=40)
    sumCount = fields.SmallIntField()

class Package(Model):
    packageId = fields.UUIDField(pk=True)
    packageName = fields.CharField(max_length=40, unique=True)
    price = fields.FloatField()
    sumNum = fields.SmallIntField()