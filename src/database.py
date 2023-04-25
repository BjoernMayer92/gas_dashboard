from sqlalchemy import create_engine, MetaData,Date, Float,Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Company(Base):
    __tablename__ = "company"
    eic = Column(String, primary_key=True)
    name = Column(String)
    short_name = Column(String)
    type = Column(String)
    country = Column(String)
    image = Column(String)
    facility = relationship("Facility", back_populates = "company")


class Facility(Base):
    __tablename__ = "facility"
    eic = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    country = Column(String)
    company_eic = Column(String, ForeignKey("company.eic"))
    company = relationship("Company", back_populates="facility")
    storage = relationship("Storage", back_populates="facility")

class Storage(Base):
    __tablename__ = "storage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gasDayStart = Column(Date)
    gasInStorage = Column(Float)
    injection = Column(Float)
    withdrawal = Column(Float)
    workingGasVolume = Column(Float)
    injectionCapacity = Column(Float)
    withdrawalCapacity = Column(Float)
    status = Column(String)
    trend = Column(Float)
    full = Column(Float)
    latitude= Column(Float)
    longitude = Column(Float)
    facility_eic = Column(String, ForeignKey("facility.eic"))
    facility = relationship("Facility", back_populates="storage")

def create_database(database_path):
    engine = create_engine("sqlite:///{}".format(database_path))
    Base.metadata.create_all(engine)