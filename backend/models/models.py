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
    packageId = fields.UUIDField(pk=True, default=uuid.uuid4)
    packageName = fields.CharField(max_length=40)
    price = fields.FloatField()
    sumNum = fields.SmallIntField()


class Plant(Model):
    plantId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plantName = fields.CharField(max_length=40, unique=True)
    plantFeature = fields.TextField()
    plantIconURL = fields.CharField(max_length=100)


class Plot(Model):
    plotId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plotName = fields.CharField(max_length=40)
    userId = fields.ForeignKeyField('models.User', related_name='plot')
    plantId = fields.ForeignKeyField('models.Plant', related_name='plot')


class Log(Model):
    logId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plotId = fields.ForeignKeyField('models.Plot', related_name='log', on_delete=fields.CASCADE)  # 级联删除
    timeStamp = fields.DatetimeField(auto_now_add=True)
    diseaseName = fields.CharField(max_length=40)
    content = fields.TextField()
    imagesURL = fields.CharField(max_length=200)


class Disease(Model):
    diseaseId = fields.UUIDField(pk=True, default=uuid.uuid4)
    plantId = fields.ForeignKeyField('models.Plant', related_name='disease', on_delete=fields.CASCADE)
    diseaseName = fields.CharField(max_length=40)
    advice = fields.TextField()
    prediction = fields.TextField(null=True)


class City(Model):
    cityCode = fields.CharField(pk=True, max_length=10)
    cityName = fields.CharField(max_length=40, unique=True)
