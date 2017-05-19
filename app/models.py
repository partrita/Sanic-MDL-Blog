# app/models.py

# 3rd party imports
import aioodbc

# local imports
from app import app


async def sql_connection():
    try:
        dsn = app.config['DB_URI']
        if not dsn:
            dsn = 'Driver=SQLite3;Database=app.db'
        return await aioodbc.connect(dsn=dsn, loop=app.loop)
    except Exception:
        print('SQL Connection Failed!')
        return False


async def sql_validate():
    if not app.config['DB_TYPE']:
        app.config['DB_TYPE'] = 'sql'
    dbtype = app.config['DB_TYPE']
    if dbtype == 'sql' or None:
        if not app.config['DB_NAME']:
            dbname = 'app.db'
        else:
            dbname = app.config['DB_NAME']
        conn = f'Driver=SQLite3;Database={dbname}'
        try:
            test = await aioodbc.connect(dsn=conn, loop=app.loop)
            if not test:
                return False
            else:
                app.config['DB_URI'] = conn
                return True
        except Exception:
            print('Exception')
            return False
    print('No DB type')
    return False


async def sql_demo():
    con = await sql_connection()
    if app.config['DEMO_CONTENT']:
        await con.execute('''CREATE TABLE "blog_posts" ( `id` INTEGER DEFAULT 'None' PRIMARY KEY AUTOINCREMENT, `post_author` VARCHAR(20) DEFAULT 'Demo', `post_date` DATETIME DEFAULT '0000-00-00 00-00-00', `post_content` TEXT DEFAULT 'None', `post_title` TEXT DEFAULT 'None', `post_name` VARCHAR(200) DEFAULT 'new post', `post_image` VARCHAR(20) DEFAULT 'road_big.jpg', `post_status` VARCHAR(20) DEFAULT 'publish', `post_modified` DATETIME DEFAULT '0000-00-00 00-00-00', `comment_status` VARCHAR(20) DEFAULT 'open', `post_password` VARCHAR(20) DEFAULT 'None', `post_likes` VARCHAR(20) DEFAULT '0' );''')
        await con.execute('''CREATE TABLE "blog_settings" ( `id` INTEGER DEFAULT 'None', `title` TEXT DEFAULT 'Blog Demo', `created_on` DATETIME DEFAULT '0000-00-00 00-00-00', `username` TEXT DEFAULT 'None', `password` VARCHAR(200) DEFAULT 'publish', `email` VARCHAR(50) DEFAULT 'None', `hidden` TEXT DEFAULT 'True', `https` TEXT DEFAULT 'off', `user_alias` VARCHAR(200) DEFAULT 'Demo', `permalink` TEXT DEFAULT '1', PRIMARY KEY(`id`) );''')
        await con.execute('''INSERT INTO "blog_posts" VALUES (1,'demo','0000-00-00 00-00-00','Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.','Coffee Pic','coffee-pic','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO "blog_posts" VALUES (2,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.','On the road again','on-the-road-again','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO "blog_posts" VALUES (3,'demo','0000-00-00 00-00-00','Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','I couldn’t take any pictures but this was an amazing thing…','i-couldnt-take-any-pictures','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.execute('''INSERT INTO "blog_posts" VALUES (4,'demo','0000-00-00 00-00-00','Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Shopping','shopping','road_big.jpg','publish','0000-00-00 00-00-00','open','None','0');''')
        await con.commit()
    else:
        await con.execute('''CREATE TABLE "blog_posts" ( `id` INTEGER DEFAULT 'None' PRIMARY KEY AUTOINCREMENT, `post_author` VARCHAR(20) DEFAULT 'Demo', `post_date` DATETIME DEFAULT '0000-00-00 00-00-00', `post_content` TEXT DEFAULT 'None', `post_title` TEXT DEFAULT 'None', `post_name` VARCHAR(200) DEFAULT 'new post', `post_image` VARCHAR(20) DEFAULT 'road_big.jpg', `post_status` VARCHAR(20) DEFAULT 'publish', `post_modified` DATETIME DEFAULT '0000-00-00 00-00-00', `comment_status` VARCHAR(20) DEFAULT 'open', `post_password` VARCHAR(20) DEFAULT 'None', `post_likes` VARCHAR(20) DEFAULT '0' )''')
        await con.execute('''CREATE TABLE "blog_settings" ( `id` INTEGER DEFAULT 'None', `title` TEXT DEFAULT 'Blog Demo', `created_on` DATETIME DEFAULT '0000-00-00 00-00-00', `username` TEXT DEFAULT 'None', `password` VARCHAR(200) DEFAULT 'publish', `email` VARCHAR(50) DEFAULT 'None', `hidden` TEXT DEFAULT 'True', `https` TEXT DEFAULT 'off', `user_alias` VARCHAR(200) DEFAULT 'Demo', `permalink` TEXT DEFAULT '1', PRIMARY KEY(`id`) )''')
        await con.commit()
    await con.close()