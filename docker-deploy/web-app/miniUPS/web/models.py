from django.db import models
from django.contrib.auth.models import User

class myUser(User):
    def __str__(self):
        return str(self.id)

class Truck(models.Model):
    __tablename__ = 'truck'

    class Meta:
       managed = False
       db_table = "truck"

    STATUS_CHOICE = (("idle", "idle"), ("driveWH", "driveWH"), ("arriveWH", "arriveWH"), ("delivering", "delivering"))
    truck_id = models.IntegerField(primary_key=True)
    whid = models.IntegerField(null=True, default=None)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    status = models.CharField(choices=STATUS_CHOICE, max_length = 128)

    def dto(self):
        ans = dict()
        ans['truck_id'] = self.truck_id
        ans['whid'] = self.whid
        ans['location_x'] = self.location_x
        ans['location_y'] = self.location_y
        ans['status'] = self.status
        return ans

class Package(models.Model):
    __tablename__ = 'package'

    class Meta:
       managed = False
       db_table = "package"

    STATUS_CHOICE = (("loaded", "loaded"), ("delivering", "delivering"), ("complete", "complete"))
    package_id = models.IntegerField(primary_key=True)
    status = models.CharField(choices=STATUS_CHOICE, max_length = 128)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    truck_id = models.IntegerField()
    email = models.CharField(max_length=256)
    item_id = models.IntegerField()
    item_num = models.IntegerField()
    item_name = models.CharField(max_length=256)
    item_desc = models.CharField(max_length=512)

    def dto(self):
        ans = dict()
        ans['package_id'] = self.package_id
        ans['status'] = self.status
        ans['location_x'] = self.location_x
        ans['location_y'] = self.location_y
        ans['truck_id'] = self.truck_id
        ans['item_id'] = self.item_id
        ans['item_num'] = self.item_num
        ans['item_name'] = self.item_name
        ans['item_desc'] = self.item_desc
        return ans