from tortoise.models import Model
from tortoise import fields

class Package(Model):
    packageId = fields.UUIDField(pk=True)
    packageName = fields.TextField()
    price = fields.FloatField()
    sumNum = fields.SmallIntField()