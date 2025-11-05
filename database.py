from sqlalchemy import text
from sqlalchemy import create_engine

engine=create_engine('sqlite:///database.db', connect_args={'check_same_thread': False} )
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS products'))
    conn.commit()
    conn.execute(text("""CREATE TABLE products (id int,
    product_code text, 
    name text, 
    short_desc text,
    regular_price int, compare_price int,
    gender text,
    highlights text,
    technology text,
    material text,
    stype text,
    usage text,
    features text,
    care text,
    images text,
    storage text)"""))
    conn.commit()

def insert_data(product_code, name, short_desc,regular_price, compare_price,gender, highlights, technology,
    material,
    stype,
    usage,
    features,
    care,
    images,
    storage):
    return None


    
    

