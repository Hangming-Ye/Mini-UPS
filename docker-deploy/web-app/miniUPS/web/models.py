from django.db import models
from django.contrib.auth.models import User
import enum

class TruckStatusEnum(enum.Enum):
    idle = 1
    driveWH = 2
    arriveWH = 3
    delivering = 4
# Create your models here.
class myUser(User):
    def __str__(self):
        return str(self.id)

class Truck(models.Model):
    __tablename__ = 'truck'


    STATUS_CHOICE = (("idle", "idle"), ("driveWH", "driveWH"), ("arriveWH", "arriveWH"), ("delivering", "delivering"))
    truck_id = models.IntegerField(primary_key=True)
    whid = models.IntegerField(null=True, default=None)
    location_x = models.IntegerField()
    location_y = models.IntegerField()
    status = models.CharField(choices=STATUS_CHOICE)

    def dto(self):
        ans = dict()
        ans['truck_id'] = self.truck_id
        ans['whid'] = self.whid
        ans['location_x'] = self.location_x
        ans['location_y'] = self.location_y
        ans['status'] = self.status
        return ans

class Package(Base):
    __tablename__ = 'package'
    package_id = Column(Integer, primary_key = True)
    status = Column(Enum(PackageStatusEnum))
    location_x = Column(Integer, nullable=True, default=None)
    location_y = Column(Integer, nullable=True, default=None)
    truck_id = Column(Integer, ForeignKey('truck.truck_id',ondelete="SET NULL", onupdate="CASCADE"))
    email = Column(String(256))
    item_id = Column(Integer)
    item_num = Column(Integer)
    item_name = Column(String(256))
    item_desc = Column(String(512))