from persistance.db import Connector
from persistance.model import TelemetryTemp

connector = Connector("sqlite:///memory")

connector.create_schema()
tlm = TelemetryTemp(name="test", value=1, ts=0, time="")
connector.insert_if_not_exists(tlm)

print("inserted")
all = connector.get_all(TelemetryTemp)
one = connector.get(TelemetryTemp(id=0))
connector.truncate(TelemetryTemp.__tablename__)
print('truncated')
dropped = connector.get_all(TelemetryTemp)
print("dropped")
