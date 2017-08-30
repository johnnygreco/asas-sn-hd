from __future__ import division, print_function


from sqlalchemy import exists
from sqlalchemy.sql import func, and_

from .tables import Run, Image, Source
from .connect import connect, Session

__all__ = ['ASHDIngest']


class ASHDIngest(object):

    def __init__(self, session, run_name):

        self.run_name = run_name 
        self.session = session
        self.current_image_id = None
        run_query = self.session.query(Run).filter(Run.name==run_name)
        num_rows = run_query.count()
        if num_rows==0:
            self.session.add(Run(name=run_name))
            self.session.commit()
            self.run_id =  self._get_current_id(Run.id)
        elif num_rows==1:
            self.run_id = run_query.first().id
        else:
            print('Warning {} rows in run name {}'.format(num_rows, run_name))

    def _get_current_id(self, table_id):
        return self.session.query(func.max(table_id)).first()[0]
        
    def add_image(self, image_label):
        image_query = self.session.query(Image).filter(
            and_(Image.label ==image_label, Image.run_id==self.run_id))
        num_rows = image_query.count()
        if num_rows==0:
            self.session.add(Image(label=image_label, run_id=self.run_id))
            self.session.commit()
            self.current_image_id = self._get_current_id(Image.id)
        elif num_rows==1:
            self.current_image_id = image_query.first().id
        else:
            print('Warning {} rows with image name {}'.format(num_rows, image_label))

    def add_catalog(self, catalog):
        """
        """
        assert self.current_image_id is not None
        catalog['image_id'] = self.current_image_id
        catalog.to_sql('source', self.session.bind, 
                       if_exists='append', index=False)

    def add_all(self, image_label, catalog): 
        self.add_image(image_label)
        self.add_catalog(catalog)
