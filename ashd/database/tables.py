from __future__ import division, print_function

import numpy as np
from sqlalchemy import String, Integer, Float, Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from .connect import Base
from astropy.coordinates import SkyCoord

__all__ = ['Run', 'Image', 'Source']

class Run(Base):
    __tablename__ = 'run'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Relationships
    images = relationship('Image', cascade='all, delete-orphan')


class Image(Base):
    __tablename__ = 'image'

    # Table columns
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    # Relationships
    run_id = Column(Integer, ForeignKey('run.id'), nullable=False)
    run = relationship('Run')
    sources = relationship('Source', cascade='all, delete-orphan')


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)
    ra =  Column(Float, nullable=False)
    dec = Column(Float, nullable=False)

    # sep paramters
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    xy = Column(Float, nullable=False)
    errx2 = Column(Float, nullable=False)
    erry2 = Column(Float, nullable=False)
    errxy = Column(Float, nullable=False)
    xmin = Column(Float, nullable=False)
    xmax = Column(Float, nullable=False)
    ymin = Column(Float, nullable=False)
    ymax = Column(Float, nullable=False)
    thresh = Column(Float, nullable=False)
    npix = Column(Integer, nullable=False)
    tnpix = Column(Integer, nullable=False)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    theta = Column(Float, nullable=False)
    cxx = Column(Float, nullable=False)
    cyy = Column(Float, nullable=False)
    cxy = Column(Float, nullable=False)
    cflux = Column(Float, nullable=False)
    flux = Column(Float, nullable=False)
    cpeak= Column(Float, nullable=False)
    peak= Column(Float, nullable=False)
    xcpeak= Column(Float, nullable=False)
    ycpeak= Column(Float, nullable=False)
    xpeak= Column(Float, nullable=False)
    ypeak= Column(Float, nullable=False)
    flag = Column(Integer, nullable=False)
    mag_auto = Column(Float, nullable=True)
    flux_auto = Column(Float, nullable=True)
    flux_radius = Column(Float, nullable=True)

    # Relationships
    image_id = Column(Integer, ForeignKey('image.id'), nullable=False)
    image = relationship('Image')

    @property
    def skycoord(self):
        return SkyCoord(ra=self.ra, dec=self.dec, unit='deg')

    @property
    def hr_angle_string(self):
        return self.skycoord.to_string('hmsdms')
