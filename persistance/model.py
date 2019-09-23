from persistance.db import Base
from sqlalchemy import Column, String, Float, Integer


class Telemetry(Base):
    __tablename__ = 'telemetry'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    ts = Column(Float)
    time = Column(String)

    def __repr__(self):
        return "<Telemetry {} - {}:{}, at {}>".format(self.id, self.name, self.value, self.time)


class TelemetryTemp(Base):
    __tablename__ = 'telemetry_temp'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    ts = Column(Float)
    time = Column(String)

    def __repr__(self):
        return "<Telemetry {} - {}:{}, at {}>".format(self.id, self.name, self.value, self.time)


class DeviceInfo(Base):
    __tablename__ = 'device_info'
    id = Column(Integer, primary_key=True)
    token = Column(String)

    def __repr__(self):
        return "<DeviceInfo {} - token: {} >".format(self.id, self.token)

