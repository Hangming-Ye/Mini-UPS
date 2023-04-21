from sqlalchemy import Column, String, Integer, ForeignKey, Double, Sequence, REAL, Enum, BIGINT
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TruckStatusEnum(enum.Enum):
    idle = 1
    driveWH = 2
    arriveWH = 3
    delivering = 4

class PackageStatusEnum(enum.Enum):
    loaded = 1
    delivering = 2
    complete = 3

class Truck(Base):
    __tablename__ = 'truck'
    truck_id = Column(Integer, primary_key = True)
    location_x = Column(Integer)
    location_y = Column(Integer)
    status = Column(Enum(TruckStatusEnum))

    def dto(self):
        ans = dict()
        ans['truck_id'] = self.truck_id
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
    time = Column(BIGINT)
    email = Column(String(256))
    item_id = Column(Integer)
    item_num = Column(Integer)
    item_name = Column(String(256))
    item_desc = Column(String(512))

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