from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Numeric

engine=create_engine('sqlite:///database.db', connect_args={'check_same_thread': False} )
metadata=MetaData()
products=Table('products', 
               metadata,
               Column('gender', Text),
               Column('masterCategory', Text),
               Column('subCategory', Text),
               Column('articleType', Text),
               Column('baseColor', Text),
               Column('season', Text),
               Column('year', Integer),
               Column('usage', Text),
               Column('productDisplayName', Text),
               Column('price', Numeric(10,2)),
               Column('product_id', Integer, primary_key=True),)
faqs=Table('faqs',
           metadata,
           Column('question', Text),
           Column('answer', Text),
           Column('type', Text))
metadata.create_all(engine)


