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
    packageName = fields.CharField(max_length=40)
    price = fields.FloatField()
    sumNum = fields.SmallIntField()


class Icon(Model):
    iconURL = fields.CharField(pk=True, max_length=100)
    iconName = fields.CharField(max_length=40)


class Plant(Model):
    plantId = fields.UUIDField(pk=True)
    plantName = fields.CharField(max_length=40)
    plantFeature = fields.TextField()


class Plot(Model):
    plotId = fields.UUIDField(pk=True)
    plotName = fields.CharField(max_length=40)
    iconURL = fields.ForeignKeyField('models.Icon', related_name='plot')
    userId = fields.ForeignKeyField('models.User', related_name='plot')
    plantId = fields.ForeignKeyField('models.Plant', related_name='plot')


class Log(Model):
    logId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plotId = fields.ForeignKeyField('models.Plot', related_name='log', on_delete=fields.CASCADE)  # 级联删除
    timeStamp = fields.DatetimeField(auto_now_add=True)
    content = fields.TextField()
    imagesURL = fields.CharField(max_length=100)


class Disease(Model):
    diseaseId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plantId = fields.ForeignKeyField('models.Plant', related_name='disease', on_delete=fields.CASCADE)
    diseaseName = fields.CharField(max_length=40)


class Advice(Model):
    diseaseId = fields.ForeignKeyField('models.Disease', pk=True, related_name='advice', on_delete=fields.CASCADE)
    content = fields.TextField()
