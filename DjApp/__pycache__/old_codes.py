'''
def add_subcategory():
    Session = sessionmaker(bind=engine)
    session = Session()

    sports = session.query(Category).filter(Category.name == 'Sports').first()
    outdoor_sports = Subcategory(name='Outdoor Sports',category=sports)
    session.add(outdoor_sports)
    session.commit()

    team_sports = Subcategory(name='Team Sports',category=sports, parent_id = outdoor_sports.id)
    session.add(team_sports)
    session.commit()

    fitness = Subcategory(name='Fitness',category=sports, parent_id = outdoor_sports.id)
    session.add(fitness)
    session.commit()

    toys = session.query(Category).filter(Category.name == 'Toys').first()
    action_figures = Subcategory(name='Action Figures',category=toys)
    session.add(action_figures)
    session.commit()

    puzzles = Subcategory(name='Puzzles',category=toys, parent_id = action_figures.id)
    session.add(puzzles)
    session.commit()

    games = Subcategory(name='Games',category=toys, parent_id = action_figures.id)
    session.add(games)
    session.commit()


def add_subcategory_with_paremetr(parent_name, new_subcategories):
    """
    This function adds new subcategories to the given parent category or subcategory.
    It first checks if the subcategory already exists in the database, and if so, it does not add it.
    :param parent_name: name of the parent category or subcategory
    :param new_subcategories: list of new subcategories to be added
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    for subcategory in new_subcategories:
        # check if the subcategory already exists in the database
        existing_category = session.query(Category).filter_by(name=subcategory).one_or_none()
        existing_subcategory = session.query(Subcategory).filter_by(name=subcategory).one_or_none()

        if existing_subcategory or existing_category:
            print(subcategory + " is already exists")
        else:
            # check if the parent category or subcategory exists in the database
            existing_parent_category = session.query(Category).filter_by(name=parent_name).one_or_none()
            existing_parent_subcategory = session.query(Subcategory).filter_by(name=parent_name).one_or_none()

            # if the parent category exists, add the new subcategory and set its parent category
            if existing_parent_category:
                new_subcategory = Subcategory(name=subcategory, category=existing_parent_category)
                session.add(new_subcategory)

            # if the parent subcategory exists, add the new subcategory and set its parent subcategory and category
            elif existing_parent_subcategory:
                new_subcategory = Subcategory(name=subcategory, subcategory=existing_parent_subcategory,
                                             category_id=existing_parent_subcategory.category_id)
                session.add(new_subcategory)

    session.commit()
    
    
def add_subcategory_without_parent():
    Session = sessionmaker(bind=engine)
session = Session()

# Adding categories
electronics = Category(name='Electronics')
smartphones = Subcategory(name='Smartphones',category=electronics)
laptops = Subcategory(name='Laptops',category=electronics)
television = Subcategory(name='Television',category=electronics)

session.add(electronics)
session.add(smartphones)
session.add(laptops)
session.add(television)
session.commit()


def add_category():
    Session = sessionmaker(bind=engine)
    session = Session()
    categories = ['Clothes','Electronics','Sports','Toys','Tools','Music']
    
    for category in categories:
        new_category = Category(name=category)
        session.add(new_category)
        session.commit()


def add_another_category():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Adding categories
    fashion = Category(name='Fashion')
    home = Category(name='Home')
    men = Subcategory(name='Men', category=fashion)
    women = Subcategory(name='Women', category=fashion)
    kids = Subcategory(name='Kids', category=fashion)
    furniture = Subcategory(name='Furniture', category=home)
    lighting = Subcategory(name='Lighting', category=home)
    kitchen = Subcategory(name='Kitchen', category=home)

    session.add(fashion)
    session.add(home)
    session.add(men)
    session.add(women)
    session.add(kids)
    session.add(furniture)
    session.add(lighting)
    session.add(kitchen)
    session.commit()


def add_new_subcategory():
    # Adding new subcategory
    Session = sessionmaker(bind=engine)
    session = Session()
    # Adding new subcategory
    television_category = session.query(Subcategory).filter(Subcategory.name == 'Television').first()
    
    smart_tv_subcategory = Subcategory(name='Non Smart TV', category_id=television_category.category_id, parent_id = television_category.id)
    session.add(smart_tv_subcategory)
    session.commit()



def add_product_to_smart():
    Session = sessionmaker(bind=engine)
    session = Session()

    oled = session.query(Subcategory).filter(Subcategory.name == 'OLED').first()
    qled = session.query(Subcategory).filter(Subcategory.name == 'QLED').first()
    lcd = session.query(Subcategory).filter(Subcategory.name == 'LCD').first()

    oled_product1 = Product(name='OLED TV1', price=1000, subcategory=oled)
    oled_product2 = Product(name='OLED TV2', price=2000, subcategory=oled)
    session.add(oled_product1)
    session.add(oled_product2)
    session.commit()

    qled_product1 = Product(name='QLED TV1', price=3000, subcategory=qled)
    qled_product2 = Product(name='QLED TV2', price=4000, subcategory=qled)
    session.add(qled_product1)
    session.add(qled_product2)
    session.commit()

    lcd_product1 = Product(name='LCD TV1', price=5000, subcategory=lcd)
    lcd_product2 = Product(name='LCD TV2', price=6000, subcategory=lcd)
    session.add(lcd_product1)
    session.add(lcd_product2)
    session.commit()


def add_subcategories_to_smart_tv():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    smart_tv = session.query(Subcategory).filter(Subcategory.name == 'Non Smart TV').first()
    OLED = Subcategory(name='OLED', parent_id = smart_tv.id)
    session.add(OLED)
    session.commit()
    
    QLED = Subcategory(name='QLED', parent_id = smart_tv.id)
    session.add(QLED)
    session.commit()
    
    LCD = Subcategory(name='LCD', parent_id = smart_tv.id)
    session.add(LCD)
    session.commit()





def add_products_pro():
    Session = sessionmaker(bind=engine)
    session = Session()

    product_names = ["Smartphone X", "Laptop Pro", "LED TV", "Sofa Set", "Dining Table Set", "King Size Bed", "Table Lamp", "Floor Lamp", "Microwave Oven", "Blender", "Men's Watch", "Women's Watch", "Kids Toy", "Outdoor Tent", "Camping Stove", "Portable Generator", "Power Drill", "Circular Saw", "Hammer", "Wrench"]

    subcategories = session.query(Subcategory).all()
    num_subcategories = len(subcategories)

    for i in range(20):
        subcategory = subcategories[i % num_subcategories]
        new_product = Product(name=product_names[i], price=25, category_id=subcategory.category_id, subcategory_id=subcategory.id)
        session.add(new_product)
    session.commit()



def add_products():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Adding products
    electronics = session.query(Category).filter(Category.name == 'Electronics').first()
    home = session.query(Category).filter(Category.name == 'Home').first()
    fashion = session.query(Category).filter(Category.name == 'Fashion').first()

    # Adding products
    product1 = Product(name='Iphone X', price=999,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Smartphones').first())
    product2 = Product(name='Samsung Galaxy S21', price=799,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Smartphones').first())
    product3 = Product(name='Macbook Pro', price=1999,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Laptops').first())
    product4 = Product(name='Sofa', price=699, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Furniture').first())
    product5 = Product(name='Dining Table', price=499, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Furniture').first())
    product6 = Product(name='Bed', price=799, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Furniture').first())
   
    # Adding products
    product7 = Product(name='LG OLED TV', price=2999,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Television').first())
    product8 = Product(name='Sony Bravia TV', price=2499,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Television').first())
    product9 = Product(name='Table Lamp', price=49, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Lighting').first())
    product10 = Product(name='Floor Lamp', price=79, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Lighting').first())
    product11 = Product(name='Microwave', price=99, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Kitchen').first())
    product12 = Product(name='Blender', price=49, subcategory=session.query(Subcategory).filter(Subcategory.name == 'Kitchen').first())
   
    # Adding products
    product13 = Product(name='Men T-Shirt', price=19.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Men').first())
    product14 = Product(name='Men Jeans', price=49.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Men').first())
    product15 = Product(name='Women Dress', price=29.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Women').first())
    product16 = Product(name='Women Skirt', price=39.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Women').first())
    product17 = Product(name='Kids T-Shirt', price=9.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Kids').first())
    product18 = Product(name='Kids Jeans', price=24.99,  subcategory=session.query(Subcategory).filter(Subcategory.name == 'Kids').first())


    session.add(product1)
    session.add(product2)
    session.add(product3)
    session.add(product4)
    session.add(product5)
    session.add(product6)
    session.add(product7)
    session.add(product8)
    session.add(product9)
    session.add(product10)
    session.add(product11)
    session.add(product12)
    session.add(product13)
    session.add(product14)
    session.add(product15)
    session.add(product16)
    session.add(product17)
    session.add(product18)


    session.commit()


def get_products_by_subcategory_name(subcategory_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    subcategory = session.query(Subcategory).filter(
        Subcategory.name == subcategory_name).first()
    subcategory_ids = [subcategory.id]
    subcategory_ids.extend(get_all_subcategory_ids(subcategory))
    products = session.query(Product).filter(
        Product.subcategory_id.in_(subcategory_ids)).all()
    return products


def get_all_subcategory_ids(subcategory):
    subcategory_ids = []
    for child in subcategory.children:
        subcategory_ids.append(child.id)
        subcategory_ids.extend(get_all_subcategory_ids(child))
    return subcategory_ids


def get_subcategory_ids(subcategory):
    
    subcategory_ids = [subcategory.id]

    print("**************************************")

    for property, value in vars(subcategory).items():
        print(property, ":", value)

    for child in subcategory.children:
        subcategory_ids.extend(get_subcategory_ids(child))
    return subcategory_ids


def get_products_by_subcategory_name(subcategory_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    subcategory = session.query(Subcategory).filter(
        Subcategory.name == subcategory_name).first()
    subcategory_ids = get_subcategory_ids(subcategory)
    products = session.query(Product).filter(
        Product.subcategory_id.in_(subcategory_ids)).all()
    return products


def get_products_by_categoy_name(subcategory_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    subcategory = session.query(Subcategory).filter(
        Subcategory.name == subcategory_name).first()
    print()
    print()
    print()
    print("************************************************")
    subcategory_ids = [subcategory.id]
    print("subcategory: ", subcategory.id)

    # subcategory_2 = [val['id'] for val in]
    ids = [val.id for val in session.query(Subcategory).filter(
        Subcategory.parent_id == subcategory.id).all()]
    print("1. val id: ", ids)

    ids = [val.id for val in session.query(Subcategory).filter(
        Subcategory.parent_id.in_(ids)).all()]
    print("2. val id: ", ids)

    # ids = [val.id for val in session.query(Subcategory).filter(Subcategory.parent_id.in_(ids)).all()]
    # print("3. val id: ",ids)

    ids = [val.name for val in session.query(Product).filter(
        Product.subcategory_id.in_(ids)).all()]

    print("All Televisions: ", ids)
    # [val['id'] for val in values]

    # ids = [id[0] for id in User.query.with_entities(Users.id).all()]

    # print("subcategory_2: ",subcategory_2)



def add_some_data():
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the categories
    electronics = Category(name='Electronics')
    clothes = Category(name='Clothes')
    session.add(electronics)
    session.add(clothes)
    session.commit()

    # Create the subcategories
    phones = SubCategory(name='Phones', category_id=electronics.id)
    laptops = SubCategory(name='Laptops', category_id=electronics.id)
    session.add(phones)
    session.add(laptops)
    session.commit()

    smartphones = SubCategory(name='Smartphones', parent_id=phones.id, category_id=electronics.id)
    classic_phones = SubCategory(name='Classic Phones', parent_id=phones.id, category_id=electronics.id)
    session.add(smartphones)
    session.add(classic_phones)
    session.commit()

    samsung = SubCategory(name='Samsung', parent_id=smartphones.id, category_id=electronics.id)
    iphone = SubCategory(name='Iphone', parent_id=smartphones.id, category_id=electronics.id)
    session.add(samsung)
    session.add(iphone)
    session.commit()

    samsung = SubCategory(name='Samsung', parent_id=classic_phones.id, category_id=electronics.id)
    iphone = SubCategory(name='Iphone', parent_id=classic_phones.id, category_id=electronics.id)
    session.add(samsung)
    session.add(iphone)
    session.commit()



'''

'''

from sqlalchemy import Table
from sqlalchemy import Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker
from DjAdvanced.settings import engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import MetaData, Table
from .helpers import GetErrorDetails


Base = automap_base()  # Create a new base class for automapping

# Prepare the automap base using the engine and reflect the tables from the database
Base.prepare(engine.engine, reflect=True)

# Map the 'category' table to the 'Category' class
Category = Base.classes.category

Product = Base.classes.product  # Map the 'product' table to the 'Product' class

# Map the 'subcategory' table to the 'Subcategory' class
Subcategory = Base.classes.subcategory


def create_tables():
    """
    This function creates the tables for the categories, subcategories, and products in the database.
    """
    class Category(Base):
        """
        This class creates the table for the categories in the database.
        """
        __table_args__ = {'extend_existing': True}
        __tablename__ = 'category'
        id = Column(Integer, primary_key=True)
        parent_id = Column(Integer, ForeignKey('category.id'))
        name = Column(String)

    class Subcategory(Base):
        """
        This class creates the table for the subcategories in the database.
        """
        __table_args__ = {'extend_existing': True}
        __tablename__ = 'subcategory'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        parent_id = Column(Integer, ForeignKey('subcategory.id'))
        category_id = Column(Integer, ForeignKey('category.id'))

    class Product(Base):
        """
        A table representing the products.
        """
        __table_args__ = {'extend_existing': True}
        __tablename__ = 'product'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        price = Column(Float)
        description = Column(String)
        subcategory_id = Column(Integer, ForeignKey('subcategory.id'))

    Base.metadata.create_all(engine)


def add_category(categories):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    Session = sessionmaker(bind=engine)  # create a new session
    session = Session()  # start a new session

    for category in categories:
        existing_category = session.query(
            Category).filter_by(name=category).one_or_none()
        existing_subcategory = session.query(
            Subcategory).filter_by(name=category).one_or_none()

        # check if a category or subcategory with the same name already exists
        if existing_category or existing_subcategory:
            print(f"{category} already exists")

        else:
            new_category = Category(name=category)
            session.add(new_category)  # add the new category to the session
            session.commit()  # commit the changes to the database


def add_subcategory(parent_name, new_subcategories):
    """
    This function adds new subcategories to the given parent category or subcategory. 
    It first checks if the subcategory or category with the same name already exists, 
    and if it does, it won't add it.
    :param parent_name: the name of the parent category or subcategory
    :type parent_name: str
    :param new_subcategories: the names of the subcategories to be added
    :type new_subcategories: list
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    for subcategory in new_subcategories:
        existing_category = session.query(Category).filter_by(
            name=subcategory).one_or_none()
        existing_subcategory = session.query(
            Subcategory).filter_by(name=subcategory).one_or_none()

        if existing_subcategory or existing_category:
            print(f"{subcategory} already exists")
        else:
            existing_parent = session.query(Category).filter_by(
                name=parent_name).one_or_none()
            existing_parent = existing_parent or session.query(
                Subcategory).filter_by(name=parent_name).one_or_none()

            if existing_parent:
                new_subcategory = Subcategory(
                    name=subcategory, parent=existing_parent)
                session.add(new_subcategory)

    session.commit()


def add_column(table_name, column_name, column_type, foreign_key=None):
    """This function add new column to table

    Args:
        table_name (string): the name of table in the database 
        column_name (string): the name of column which you want add to table
        column_type (any): the type of the added column 
        foreignKey (str, optional): if column type is foreignKey, please input . Defaults to None.
    """
    # checking added column is foreign_key or not.
    if foreign_key:
        column = Column('column_name', column_type, ForeignKey(foreign_key))
    else:
        column = Column('column_name', column_type)

    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    # adding new column
    engine.execute('ALTER TABLE %s ADD COLUMN %s %s' %
                   (table_name, column_name, column_type))


def add_products_to_subcategory(subcategory_name, product_list):
    """
    This function is used to add products to a specific subcategory. 
    It checks if a product with the same name already exists in the database and if so, it does not add it.
     Parameters:
        subcategory_name (str): The name of the subcategory to add the products to.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', and 'description'.   
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    subcategory = session.query(Subcategory).filter(
        (Subcategory.name == subcategory_name)).first()

    # Iterate through the list of products
    for product in product_list:
        # Check if a product with the same name already exists
        existing_product = session.query(Product).filter_by(
            name=product['name']).one_or_none()

        if existing_product:
            print(f"{product['name']} already exists")
        else:
            new_product = Product(name=product['name'], price=product['price'],
                                  description=product['description'], subcategory=subcategory)
            session.add(new_product)

    # Commit the changes to the database
    session.commit()


def delete_all_tables():
    """ 
    This function deletes all tables.
    """
    Base.metadata.drop_all(bind=engine)


def delete_null_category_subcategories():
    """
    This function deletes all subcategories that have a null category_id.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    # query to get all products that have a null subcategory_id
    null_category_subcategories = session.query(
        Subcategory).filter(Subcategory.category_id == None).all()
    # Iterate through the products and delete them one by one
    for category in null_category_subcategories:
        session.delete(category)
        session.commit()
        print(
            f"Deleted {len(null_category_subcategories)} products with null subcategory_id")
        # Return the number of deleted products for confirmation
    return len(null_category_subcategories)


def delete_null_subcategory_products():
    """
    This function deletes all products that have a null subcategory_id.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    # query to get all products that have a null subcategory_id
    null_subcategory_products = session.query(
        Product).filter(Product.subcategory_id == None).all()
    # Iterate through the products and delete them one by one
    for product in null_subcategory_products:
        session.delete(product)
        session.commit()
        print(
            f"Deleted {len(null_subcategory_products)} products with null subcategory_id")
        # Return the number of deleted products for confirmation
    return len(null_subcategory_products)


def get_all_products_by_subcategory_name(category_name):
    """
    This function returns all products belong to a subcategory by given subcategory name
    :param subcategory_name: str, name of the subcategory
    :return: list of Product objects
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    existing_category = session.query(Category).filter_by(name=category_name).one_or_none()
    existing_category = existing_category or session.query(Subcategory).filter_by(name=category_name).one_or_none()
    
    if existing_category:
        all_products = session.query(Product).filter_by(subcategory_id = existing_category.id).all()
    else:
        return ["It is empty"]
        
    return all_products


def get_products_by_category_name(category_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    category = session.query(Category).filter(Category.name == category_name).first()
    subcategory_ids = session.query(Subcategory.id).filter(Subcategory.category_id == category.id).all()
    subcategory_ids = [id[0] for id in subcategory_ids]
    # subcategory_ids = [subcategory.id for subcategory in category.subcategories]
    subcategory_ids.extend(get_all_subcategory_ids(category))
    products = session.query(Product).filter(Product.subcategory_id.in_(subcategory_ids)).all()
    return products

def get_all_subcategory_ids(category):
    subcategory_ids = []
    Session = sessionmaker(bind=engine)
    session = Session()

    all_subcategories = session.query(Subcategory).filter_by(category_id=category.id).all()
    for subcategory in all_subcategories:
        subcategory_ids.append(subcategory.id)
        subcategory_ids.extend(get_all_subcategory_ids(subcategory))
    return subcategory_ids




# products = get_products_by_category_name("Music")
# for a in products:
#     print(a.name)


# add_category()
# creat_tables()
# delete_all_tables()
# add_subcategory()
# add_subcategory_without_parent()
# add_subcategory_with_paremetr(parent_name, subcategory_name)
# add_another_category()
# add_products()
# delete_null_category_products()
# add_new_subcategory()
# add_column(table_name)
# add_products_pro()
# add_subcategories_to_smart_tv()


# category_name = "Furniture"
# all_products = get_all_products_by_category_name(category_name)
# for product in all_products:
#     print(product.name)


# example usage
# add_products_to_subcategory('H.O.S.T', [{'name': 'Red in black', 'price': 0, 'description': 'Song'}, {'name': 'Propaganda', 'price': 0, 'description': 'Song'}])

# add_product_to_smart()




def add_products_to_subcategory(subcategory_name, product_list):
    """
    This function is used to add products to a specific subcategory. 
    It checks if a product with the same name already exists in the database and if so, it does not add it.
     Parameters:
        subcategory_name (str): The name of the subcategory to add the products to.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', and 'description'.   
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    subcategory = session.query(Subcategory).filter(
        (Subcategory.name == subcategory_name)).first()

    # Iterate through the list of products
    for product in product_list:
        # Check if a product with the same name already exists
        existing_product = session.query(Product).filter_by(
            name=product['name']).one_or_none()

        if existing_product:
            print(f"{product['name']} already exists")
        else:
            new_product = Product(name=product['name'], price=product['price'],
                                  description=product['description'], subcategory=subcategory)
            session.add(new_product)

    # Commit the changes to the database
    session.commit()




    # json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
    # try:
    #    print("json_data:", json_data)
        
    #    data = json_data['data']
    #    print("data:", data)
    # except KeyError:
    #     print("keyError")
   
   
   
   


add_new_permission("Delete products","Allows a user to delete products from the website.")
add_new_permission("View orders","Ability to view the list of orders placed by customers, including the order details and status.")
add_new_permission("Process orders","This permission allows a user to process orders placed on the e-commerce website. This includes tasks such as updating order status, payment processing, and shipping information.")
add_new_permission("Update Order","Ability to update the status of an order, for example, from Pending to Shipped or Delivered.")
add_new_permission("Cancel orders","This permission allows a user to cancel orders that have been placed on the e-commerce website. This may be required in cases where the customer changes their mind or the order cannot be fulfilled.")
add_new_permission("Refund orders","Ability to process refunds for customers, for example, when a product is damaged or the customer has changed their mind.")
add_new_permission("Manage orders","Allows a user to view, process, and manage orders on the website.")
add_new_permission("Manage customers","Allows a user to view and manage customer information on the website.")
add_new_permission("Manage discounts","Allows a user to manage discounts and promo codes on the website.")
add_new_permission("Manage shipping","Allows a user to manage shipping options and shipping rates on the website.")
add_new_permission("Manage payment","Allows a user to manage payment options and payment processing on the website.")
add_new_permission("View reports","Allows a user to view and generate various reports related to sales, customers, and products on the website.")
add_new_permission("Generate reports"," This permission allows a user to generate reports on various aspects of the e-commerce website. This may include sales reports, customer reports, and product reports.")
add_new_permission("Export reports","This permission allows a user to export reports generated on the e-commerce website. This may include exporting reports to a variety of formats such as CSV, PDF, or Excel.")
add_new_permission("Manage website content","Ability to manage and update the website content, including pages, images, and blog posts.")
add_new_permission("Manage website settings","Ability to manage and configure system-wide settings, including security and performance settings.")
add_new_permission("Manage website design","Ability to customize the website design and layout, including themes, colors, and fonts.")
add_new_permission("Manage website themes"," This permission allows the user to add, edit, and delete themes on the website, as well as activate and deactivate them.")
add_new_permission("Manage website plugins.","This permission allows the user to install, configure, and manage plugins on the website, including adding and removing them, as well as activating and deactivating them.")




role_names = ['Administrator', 'Customer Service Representative', 'Marketing Manager', 'Product Manager', 'Sales Manager', 'Warehouse Manager', 'Shipping Coordinator', 'Payment Specialist', 'Website Manager', 'Customer']
role_descriptions = ['Responsible for managing the overall operations of the e-commerce website', 
                     'Responsible for providing customer support and addressing customer complaints', 
                     'Responsible for planning and executing marketing campaigns', 
                     'Responsible for managing and updating products on the website', 
                     'Responsible for managing sales and revenue goals', 
                     'Responsible for managing the inventory and shipping process', 
                     'Responsible for coordinating shipments and delivery of orders', 
                     'Responsible for managing the payment process and resolving payment issues', 
                     'Responsible for managing the overall design and functionality of the website', 
                     'Regular customer of the e-commerce website']

for i in range(len(role_names)):
    add_new_role(role_names[i], role_descriptions[i])
 
 
 
 
 
 
 
 
id role_id permission_id
11	7	3
12	7	4
14	7	3
15	7	4
17	7	3
18	7	13  
19	7	11
20	7	4
21	7	12
22	7	16
23	7	18
24	7	17
25	7	19
26	7	20
27	7	21
28	7	22
29	7	23
30	7	24
31	7	25
32	7	26
33	7	27
34	7	28
35	7	29
36	7	30
37	7	31
38	7	32
39	7	33
40	7	34
41	8	3
42	8	11
43	8	18
44	8	19
45	8	20
46	8	21
47	8	22
48	9	3
49	9	11
50	9	27
51	9	28
52	9	29
53	10	3
54	10	11
55	10	4
56	10	12
57	10	16
58	11	3
59	11	11
60	11	18
61	11	17
62	11	19
63	11	20
64	12	3
65	12	11
66	12	25
67	13	3
68	13	11
69	13	25
70	14	3
71	14	11
72	14	26
73	15	3
74	15	11
75	15	30
76	15	31
77	15	32
78	15	33
79	15	34
80	16	3
81	16	11




# Define a list of permissions
  
permission= [
{'id': 3, 'name': "read"},          
{'id': 13, 'name': "delete"}, 
{'id': 11, 'name': "view products"},  
{'id': 4, 'name': "add products"},  
{'id': 12, 'name': "edit products"},  
{'id': 16, 'name': "Delete products"},  
{'id': 18, 'name': "View orders"}, 
{'id': 17, 'name': "Process orders"}, 
{'id': 19, 'name': "Update Order"}, 
{'id': 20, 'name': "Cancel orders"},  
{'id': 21, 'name': "Refund orders"}, 
{'id': 22, 'name': "Manage orders"},  
{'id': 23, 'name': "Manage customers"},  
{'id': 24, 'name': "Manage discounts"},  
{'id': 25, 'name': "Manage shipping"},  
{'id': 26, 'name': "Manage payment"},  
{'id': 27, 'name': "View reports"},  
{'id': 28, 'name': "Generate reports"},  
{'id': 29, 'name': "Export reports"},  
{'id': 30, 'name': "Manage website content"},  
{'id': 31, 'name': "Manage website settings"},  
{'id': 32, 'name': "Manage website design"}, 
{'id': 33, 'name': "Manage website themes"}, 
{'id': 34, 'name': "Manage website plugins"}, 
]

# Roles and their respective permissions
role_permissions = {
    "Administrator": [3, 13, 11, 4, 12, 16, 18, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
    "Customer Service Representative": [3, 11, 18, 19, 20, 21, 22],
    "Marketing Manager": [3, 11, 27, 28, 29],
    "Product Manager": [3, 11, 4, 12, 16],
    "Sales Manager": [3, 11, 18, 17, 19, 20],
    "Warehouse Manager": [3, 11, 25],
    "Shipping Coordinator": [3, 11, 25],
    "Payment Specialist": [3, 11, 26],
    "Website Manager": [3, 11, 30, 31, 32, 33, 34],
    "Customer": [3, 11]
}

# Add role-permission relations to the database
for role_name, permission_ids in role_permissions.items():
    for permission_id in permission_ids:
        add_new_role_permission(role_name, permission_id)

 
 
add_user_groups([{"name": "Administrators", "description": "Have access to all areas of the site"}])
 
 
 

def random_string(stringLength=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

for i in range(1,21):
    username = "user" + str(i)
    usermail = username + "@example.com"
    password = "password" + str(i)
    first_name = random_string(5)
    last_name = random_string(7)
    telephone = random.randint(1000000000, 9999999999)
    add_user(username,usermail,password,first_name,last_name,telephone)




def distribute_users():
    Session = sessionmaker(bind=engine)
    session = Session()
        
    # The groups and roles that are compatible with each other
    group_role_mapping = {
        19: [7], # Administrators Group => Administrator Role
        20: [16], # Customers Group => Customer Role
        21: [7], # Moderators Group => Administrator Role
        22: [10], # Product Managers Group => Product Manager Role
        23: [11], # Sales Representatives Group => Sales Manager Role
        24: [9], # Marketing Team Group => Marketing Manager Role
        25: [8], # Customer Support Group => Customer Service Representative Role
        26: [13], # Shipping and Logistics Team Group => Shipping Coordinator Role
        27: [14], # Payment and Security Team Group => Payment Specialist Role
        28: [7], # Data Analysts Group => Administrator Role
        29: [12], # Inventory Managers Group => Warehouse Manager Role
        30: [7], # Technical Support Group => Administrator Role
        31: [7], # Operations Team Group => Administrator Role
    }

    user_ids = [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]

    for user_id in user_ids:
        # Get a random group id from the mapping dictionary
        group_id = list(group_role_mapping.keys())[randint(0, len(group_role_mapping) - 1)]
        # Get the compatible role id for the selected group
        role_id = group_role_mapping[group_id][randint(0, len(group_role_mapping[group_id]) - 1)]
        # Add the user to the user_user_group_role table
        user_user_group_role = UserUserGroupRole(
            user_id=user_id,
            user_group_id=group_id,
            role_id=role_id
        )
        session.add(user_user_group_role)

    session.commit()


# distribute_users()
 
 
 
 
 
        
# @login_required(login_url='login')
# def home (request):
    # orders = Order.objects.all()
    # customers Customer.objects.all()
    # total_customers = customers.count()
    # total_orders = orders.count() 
    # delivered = orders.filter(status = 'Delivered').count() pending = orders.filter(status = 'Pending').count()
    # context = {'orders': orders, 'customers': customers, 'total_orders': total_orders, 'delivered' : delivered, 'pending': pending }
    # return render(request, 'accounts/dashboard.html', context)



# @csrf_exempt
# @permission_required('app_name.view_resource', raise_exception=True)
# def view_resource(request, resource_id):
#     print("its work")
#     return JsonResponse({"message":"success"},status=200)



# @csrf_exempt
# def check_user(request):
#     username = request.POST.get('username'); 
#     usermail = request.POST.get('usermail'); 
#     password = request.POST.get('password'); 

#     user = authenticate(username=username, password=password)
#     if user is not None:
#         return JsonResponse({"message": "you have not access"},status=200)
#         # A backend authenticated the credentials
#     else:
#         # No backend authenticated the credentials
#         return JsonResponse({"message": "you are success"},status=200)
        
        
        
        def token_required(func):
        """
    A decorator function that verifies the authenticity of the JWT token and username.

    This function checks if the `token` and `username` are present in the request.
    If either of them is missing, it returns a JSON response with status 401 (Unauthorized).
    Then, it decodes the token using the secret key. If the token is invalid or has expired, it returns a JSON response with status 401.
    If the decoded token's `username` does not match the `username` in the request, it returns a JSON response with status 401.
    Finally, it retrieves the user with the `username` from the database and adds it to the request object as `request.user`.
    If the user does not exist, it returns a JSON response with status 401.

    Args:
        func (function): The view function that this decorator wraps.

    Returns:
        wrapper (function): The decorated function.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Get the token and username from the request
        if request.method == 'POST':
            input_token = request.POST.get('token')
            username = request.POST.get('username')
        else:
            input_token = request.GET.get('token')
            username = request.GET.get('username')
        
        # Check if either the token or username is missing
        if not input_token or not username:
            return JsonResponse({'message': 'Missing token or username'}, status=401)
        
        try:
            # Try to decode the token
            decoded = jwt.decode(input_token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': True})
            
            # Check if the username in the request matches the decoded token's username
            if username != decoded['username']:
                return JsonResponse({'message': 'Token username mismatch'}, status=401)
            
            # Get the user with the username from the database
            try:
                user = Users.objects.get(token=input_token)
            except Users.DoesNotExist:
                return JsonResponse({'message': 'User does not exist'}, status=401)
            
        except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.InvalidTokenError):
            return JsonResponse({'message': 'Invalid or expired token'}, status=401)
        
        # Add the user to the request object
        request.user = user
        
        return func(request, *args, **kwargs)
    
    return wrapper






    # Download the helper library from https://www.twilio.com/docs/python/install
    import os
    from twilio.rest import Client

    # Set environment variables for your credentials
    # Read more at http://twil.io/secure
    account_sid = "AC6e16020f8aa1c283d8c95ba7b811ac75"
    auth_token = "2c40a1e5318707bfcc7388bbbf36374c"
    verify_sid = "VA7a9e3997c0507d137ee72a3d1e648572"
    verified_number = "+994703335610"

    client = Client(account_sid, auth_token)

    verification = client.verify.v2.services(verify_sid) \
    .verifications \
    .create(to=verified_number, channel="sms")
    print(verification.status)

    otp_code = input("Please enter the OTP:")

    verification_check = client.verify.v2.services(verify_sid) \
    .verification_checks \
    .create(to=verified_number, code=otp_code)
    print(verification_check.status)


'''