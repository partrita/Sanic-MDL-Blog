#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import urandom, path

import aioodbc
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import file, redirect
from sanic_compress import Compress
from sanic_jinja2 import SanicJinja2
from sanic_session import InMemorySessionInterface
from sanic_useragent import SanicUserAgent

from forms import WelcomeForm, DatabaseForm, LoginForm

app = Sanic(__name__)
jinja = SanicJinja2(app)
Compress(app)
session = InMemorySessionInterface(expiry=600)
SanicUserAgent.init_app(app, default_locale='en_US')


@app.listener('before_server_start')
async def setup_cfg(app, loop):
    try:
        cfg = app.config.from_pyfile('config.py')
        if cfg is None:
            app.config.from_envvar('MY_SETTINGS')
    except FileNotFoundError:
        app.config['SECRET_KEY'] = urandom(24)
        app.config['DEMO_CONTENT'] = True
        print('Warning - Config Not Found. Using Defaults.')
    if path.isfile('app.db'):
        app.config['SETUP_DB'] = False
        app.config['SETUP_BLOG'] = False
        app.config['DB_URI'] = 'Driver=SQLite3;Database=app.db'
    else:
        app.config['SETUP_DB'] = True
        app.config['SETUP_BLOG'] = True


@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('Server successfully started.')


@app.listener('before_server_stop')
async def notify_server_stopping(app, loop):
    print('Server shutting down...')


@app.listener('after_server_stop')
async def close_db(app, loop):
    print('Server successfully shutdown.')


@app.middleware('request')
async def add_session_to_request(request):
    await session.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session.save(request, response)


@app.exception(NotFound)
async def ignore_404s(request, exception):
    page = dict()
    page['title'] = '404 Error'
    page['header'] = '404 Error - Page Not Found'
    page['text'] = 'We Can\'t Seem To Find ' + request.url
    return jinja.render('page.html', request, page=page)


async def check(connection):
    try:
        checking = await aioodbc.connect(dsn=connection)
        if not checking:
            return False
        else:
            return True
    except Exception:
        print(Exception)


async def db_connection():
    dsn = 'Driver=SQLite3;Database=app.db'
    return await aioodbc.connect(dsn=dsn, loop=app.loop)
    # dbtype = app.config['DB_TYPE']
    # if dbtype is 'sql' or None:
    #     if app.config['DB_URI']:
    #         dsn = app.config['DB_URI']
    #     else:
    #         dsn = 'Driver=SQLite3;Database=sqlite.db'
    #     check = await aioodbc.connect(dsn=dsn, loop=app.loop)
    #     if not check:
    #         dsn = 'Driver=SQLite3;Database=sqlite.db'
    #     print(dsn)
    #     return await aioodbc.connect(dsn=dsn, loop=app.loop)
    # elif dbtype is 'post':
    #     return
    # elif dbtype is 'mysql':
    #     return


async def is_setup():
    stp = app.config['SETUP_BLOG']
    dbs = app.config['SETUP_DB']
    if stp and dbs:
        return 'setup-db'
    if stp and not dbs:
        return 'setup-blog'
    if not stp and not dbs:
        return True


async def db_setup():
    con = await db_connection()
    cur = await con.cursor()
    if app.config['DEMO_CONTENT']:
        await cur.execute('DROP TABLE IF EXISTS blog_posts;')
        await cur.commit()
        await cur.execute('CREATE TABLE IF NOT EXISTS blog_posts ('
                          'Id INTEGER PRIMARY KEY,'
                          'post_author VARCHAR(20) DEFAULT "demo",'
                          'post_date DATETIME DEFAULT "0000-00-00 00-00-00",'
                          'post_content TEXT DEFAULT "None",'
                          'post_title TEXT DEFAULT "None",'
                          'post_name VARCHAR(200) DEFAULT "new post",'
                          'post_excerpt TEXT DEFAULT "None",'
                          'post_image VARCHAR(20) DEFAULT "road_big.jpg",'
                          'post_status VARCHAR(20) DEFAULT "publish",'
                          'post_modified DATETIME DEFAULT "0000-00-00 00-00-00",'
                          'comment_status VARCHAR(20) DEFAULT "open",'
                          'post_password VARCHAR(20) DEFAULT "None",'
                          'post_likes VARCHAR(20) DEFAULT "0" );')
        await cur.commit()
        await cur.execute('DROP TABLE IF EXISTS blog_settings;')
        await cur.commit()
        await cur.execute('CREATE TABLE IF NOT EXISTS blog_settings ('
                          'id INTEGER PRIMARY KEY,'
                          'title TEXT default "Blog Demo",'
                          'created_on DATETIME default "0000-00-00 00-00-00",'
                          'username TEXT default "None",'
                          'password VARCHAR(200) default "publish",'
                          'email VARCHAR(50) default "None",'
                          'hidden TEXT default "True",'
                          'https TEXT default "off",'
                          'user_alias VARCHAR(200) default "Demo",'
                          'permalink TEXT default "1";')
        await cur.commit()
        await cur.execute('SELECT * FROM blog_posts;')
        data = await cur.fetchone()
        if not data:
            await cur.execute(
                '''INSERT INTO `blog_posts` VALUES (1,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.<br /><br /><br />Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.<br /><br /><br />Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Coffee Pic','coffee-pic','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','coffee.jpg','publish','0000-00-00 00-00-00','open','None','60');''')
            await cur.execute(
                '''INSERT INTO `blog_posts` VALUES (2,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.<br /><br /><br />Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.<br /><br /><br />Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','On the road again','on-the-road-again','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','50');''')
            await cur.execute(
                '''INSERT INTO `blog_posts` VALUES (3,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.<br /><br /><br />Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.<br /><br /><br />Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','I couldn’t take any pictures but this was an amazing thing…','i-couldnt-take-any-pictures','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','road_big.jpg','publish','0000-00-00 00-00-00','open','None','40');''')
            await cur.execute(
                '''INSERT INTO `blog_posts` VALUES (4,'demo','0000-00-00 00-00-00','Excepteur reprehenderit sint exercitation ipsum consequat qui sit id velit elit. Velit anim eiusmod labore sit amet. Voluptate voluptate irure occaecat deserunt incididunt esse in. Sunt velit aliquip sunt elit ex nulla reprehenderit qui ut eiusmod ipsum do. Duis veniam reprehenderit laborum occaecat id proident nulla veniam. Duis enim deserunt voluptate aute veniam sint pariatur exercitation. Irure mollit est sit labore est deserunt pariatur duis aute laboris cupidatat. Consectetur consequat esse est sit veniam adipisicing ipsum enim irure.<br /><br /><br />Qui ullamco consectetur aute fugiat officia ullamco proident Lorem ad irure. Sint eu ut consectetur ut esse veniam laboris adipisicing aliquip minim anim labore commodo. Incididunt eu enim enim ipsum Lorem commodo tempor duis eu ullamco tempor elit occaecat sit. Culpa eu sit voluptate ullamco ad irure. Anim commodo aliquip cillum ea nostrud commodo id culpa eu irure ut proident. Incididunt cillum excepteur incididunt mollit exercitation fugiat in. Magna irure laborum amet non ullamco aliqua eu. Aliquip adipisicing dolore irure culpa aute enim. Ullamco quis eiusmod ipsum laboris quis qui.<br /><br /><br />Cillum ullamco eu cupidatat excepteur Lorem minim sint quis officia irure irure sint fugiat nostrud. Pariatur Lorem irure excepteur Lorem non irure ea fugiat adipisicing esse nisi ullamco proident sint. Consectetur qui quis cillum occaecat ullamco veniam et Lorem cupidatat pariatur. Labore officia ex aliqua et occaecat velit dolor deserunt minim velit mollit irure. Cillum cupidatat enim officia non velit officia labore. Ut esse nisi voluptate et deserunt enim laborum qui magna sint sunt cillum. Id exercitation labore sint ea labore adipisicing deserunt enim commodo consectetur reprehenderit enim. Est anim nostrud quis non fugiat duis cillum. Aliquip enim officia ad commodo id.','Shopping','shopping','Enim labore aliqua consequat ut quis ad occaecat aliquip incididunt. Sunt nulla eu enim irure enim nostrud aliqua consectetur ad consectetur sunt ullamco officia. Ex officia laborum et consequat duis.','shopping.jpg','publish','0000-00-00 00-00-00','open','None','30');''')
            await cur.commit()
        await cur.close()
        await con.close()
    else:
        await cur.execute('CREATE TABLE IF NOT EXISTS blog_posts ('
                          'Id INTEGER PRIMARY KEY,'
                          'post_author UNSIGNED BIG INT(20) default "0",'
                          'post_date DATETIME default "0000-00-00 00-00-00",'
                          'post_content TEXT default "None",'
                          'post_title TEXT default "None",'
                          'post_excerpt TEXT default "None",'
                          'post_status VARCHAR(20) default "publish",'
                          'post_modified DATETIME NOT NULL,'
                          'comment_status VARCHAR(20) default "open",'
                          'post_password VARCHAR(20) NOT NULL,'
                          'post_name VARCHAR(200) NOT NULL,'
                          'post_likes VARCHAR(20) NOT NULL);')
        await cur.execute('CREATE TABLE IF NOT EXISTS blog_settings ('
                          'id INTEGER PRIMARY KEY,'
                          'title TEXT default "Blog Demo",'
                          'created_on DATETIME default "0000-00-00 00-00-00",'
                          'username TEXT default "None",'
                          'password VARCHAR(200) default "publish",'
                          'email VARCHAR(50) default "None",'
                          'hidden TEXT default "True",'
                          'https TEXT de        fault "off",'
                          'user_alias VARCHAR(200) default "Demo",'
                          'permalink TEXT default "1";')
        await cur.commit()
        await con.close()


async def setup_blog(request):
    # issetup = await is_setup()
    # if not issetup:
    #     return redirect(issetup)
    page = dict()
    form = WelcomeForm(request)
    if request.method == 'POST' and form.validate():
        con = await db_connection()
        cur = await con.cursor()
        await cur.execute(
            f'INSERT INTO blog_settings (title,username,password,email,hidden) VALUES ({form.title.data},{form.username.data},{form.password.data},{form.email.data},{form.seo.data})')
        # TODO: if valid information, redirect to home, save all created variables from welcome form data to db
        request['session']['username'] = form.username.data
        app.config['SETUP_BLOG'] = False
        uri = app.config['DB_URI']
        dbt = app.config['DB_TYPE']
        with open("config.py", "wt") as o:
            o.write(f'DB_URI = {repr(uri)}\n')
            o.write(f'DB_TYPE = {repr(dbt)}\n')
        await db_setup()
        return redirect('/')
    page['title'] = 'Blog First Start'
    page['header'] = 'Welcome'
    page['text'] = 'Before you get blogging, we need to setup a few things.'
    return jinja.render('page.html', request, page=page, form=form)


async def setup_db(request):
    # issetup = await is_setup()
    # if not issetup:
    #     return redirect(issetup)
    page = dict()
    form = DatabaseForm(request)
    if request.method == 'POST' and form.validate():
        app.config['DB_NAME'] = form.username.data
        app.config['DB_PASSWORD'] = form.password.data
        app.config['DB_URI'] = form.host.data
        if not app.config['DB_URI']:
            app.config['DB_URI'] = 'Driver=SQLite3;Database=app.db'
        app.config['DB_TYPE'] = form.dbtype.data
        dsn = app.config['DB_URI']
        valid = await check(dsn)
        if not valid:
            print('invalid db connection')
            return redirect('setup-db')
        app.config['SETUP_DB'] = False
        return redirect('setup-blog')
    page['title'] = 'Blog First Start'
    page['header'] = 'Setup Database'
    page['text'] = 'Below you should enter your database connection details.'
    return jinja.render('page.html', request, page=page, form=form)


async def index(request):
    if app.config['SETUP_BLOG']:
        return redirect('setup-db')
    con = await db_connection()
    cur = await con.cursor()
    await cur.execute('SELECT * FROM blog_posts;')
    fetch = await cur.fetchmany(4)
    if fetch is None:
        page = dict()
        page['post_title'] = 'No Posts Found :('
        page['post_excerpt'] = 'Sorry, We couldn\'t find any posts.'
        return jinja.render('index.html', request, page=page)
    await cur.close()
    await con.close()
    return jinja.render('index.html', request, page=fetch)


async def post(request, name):
    if app.config['SETUP_BLOG']:
        return redirect('setup-db')
    con = await db_connection()
    cur = await con.cursor()
    await cur.execute(f'SELECT * FROM blog_posts WHERE post_name="{name}";')
    fetch = await cur.fetchone()
    if not fetch:
        raise NotFound("404 Error", status_code=404)
    await cur.close()
    await con.close()
    return jinja.render('post.html', request, post=fetch)


async def dashboard(request):
    cookie_check = request['session'].get('username')
    if cookie_check is None:
        return redirect('login')
    return jinja.render('admin.html', request, pagename='Dashboard')


async def login(request):
    if app.config['SETUP_BLOG']:
        return redirect('setup-db')
    page = dict()
    form = LoginForm(request)
    if request.method == 'POST' and form.validate():
        fuser = form.username.data
        fpass = form.password.data
        con = await db_connection()
        cur = await con.cursor()
        await cur.execute(f'SELECT * FROM blog_settings WHERE username="{fuser}";')
        get_user = await cur.fetchone()
        await cur.execute(f'SELECT * FROM blog_settings WHERE password="{fpass}";')
        get_pass = await cur.fetchone()
        if get_user == fuser and get_pass == fpass:
            request['session']['username'] = get_user
            page['title'] = 'Login'
            page['header'] = 'Thank you for logging in!'
            page['text'] = 'Redirecting in 3 seconds...'
            return jinja.render('page.html', request, page=page,
                                js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; }'
                                            ',3000);</script>')
    login_check = request['session'].get('username')
    if login_check is None:
        stp = app.config['SETUP_BLOG']
        if stp:
            return redirect('setup-blog')
        page['title'] = 'Login'
        page['header'] = 'Restricted Area - Login Required'
        return jinja.render('page.html', request, page=page, form=form,
                            css_head_end='<style>.mdl-layout{align-items: center;justify-content: center;}'
                                         '.mdl-layout__content {padding: 24px;flex: none;}</style>')
    page['title'] = 'Login'
    page['header'] = 'You\'re already logged in!'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "admin"; },3000);'
                                    '</script>')


async def logout(request):
    page = dict()
    del request['session']['username']
    page['title'] = 'Logging Out'
    page['header'] = 'You have been successfully logged out'
    page['text'] = 'Redirecting in 3 seconds...'
    return jinja.render('page.html', request, page=page,
                        js_head_end='<script defer>window.setTimeout(function(){ window.location = "/"; }'
                                    ',3000);</script>')


# This is only for testing, nothing useful for average user
async def test(request):
    raise NotFound("Something bad happened", status_code=404)


async def images(request, name):
    return await file('images/' + name)


async def styles(request):
    return await file('css/styles.css')


async def admin_styles(request):
    return await file('/css/admin.css')


async def redirect_index(request):
    return redirect('/')


app.add_route(setup_blog, 'setup-blog', methods=['GET', 'POST'])
app.add_route(setup_db, 'setup-db', methods=['GET', 'POST'])
app.add_route(test, 'test')
app.add_route(index, '/')
app.add_route(images, 'images/<name>')
app.add_route(styles, 'styles.css')
app.add_route(admin_styles, 'admin.css')
app.add_route(post, '/<name>')
app.add_route(dashboard, 'admin')
app.add_route(login, 'login', methods=['GET', 'POST'])
app.add_route(logout, 'logout')
app.add_route(redirect_index, '/index.html')

app.run(host='127.0.0.1', port=8000, debug=True)
