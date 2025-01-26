import apsw
from loguru import logger

from . import app_globals as ag

TABLES = (
    (                # settings
    'CREATE TABLE IF NOT EXISTS settings ('
    'key text NOT NULL, '
    'value blob); '
    ),
    (                # files
    'CREATE TABLE IF NOT EXISTS files ('
    'id integer PRIMARY KEY NOT NULL, '
    'extid integer NOT NULL, '
    'path integer NOT NULL, '
    'filename text NOT NULL, '
    'modified date not null default -62135596800, '
    'opened date not null default -62135596800, '
    'created date not null default -62135596800, '
    'rating integer not null default 0, '
    'nopen integer not null default 0, '
    'hash text, '
    'size integer not null default 0, '
    'pages integer not null default 0, '
    'published date not null default -62135596800, '
    'FOREIGN KEY (extid) REFERENCES extensions (id)); '
    ),
    (                # dirs
    'CREATE TABLE IF NOT EXISTS dirs ('
    'id integer PRIMARY KEY NOT NULL, '
    'name text); '
    ),
    (                # paths
    'CREATE TABLE IF NOT EXISTS paths ('
    'id integer PRIMARY KEY NOT NULL, '
    'path text); '
    ),
    (                # filedir
    'CREATE TABLE IF NOT EXISTS filedir ('
    'file integer NOT NULL, '
    'dir integer NOT NULL, '
    'PRIMARY KEY(dir, file), '
    'FOREIGN KEY (dir) REFERENCES dirs (id) on delete cascade, '
    'FOREIGN KEY (file) REFERENCES files (id) on delete cascade); '
    ),
    (                # parentdir
    'CREATE TABLE IF NOT EXISTS parentdir ('
    'parent integer NOT NULL, '
    'id integer NOT NULL, '
    'multy integer not null default 0, '
    'hide integer not null default 0, '
    'file_id integer not null default 0, '
    'tool_tip text, '
    'PRIMARY KEY(parent, id)); '
    ),
    (                # tags
    'CREATE TABLE IF NOT EXISTS tags ('
    'id integer PRIMARY KEY NOT NULL, '
    'tag text NOT NULL); '
    ),
    (                # filetag
    'CREATE TABLE IF NOT EXISTS filetag ('
    'fileid integer NOT NULL, '
    'tagid integer NOT NULL, '
    'PRIMARY KEY(fileid, tagid), '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade, '
    'FOREIGN KEY (tagid) REFERENCES tags (id) on delete cascade); '
    ),
    (                # authors
    'CREATE TABLE IF NOT EXISTS authors ('
    'id integer PRIMARY KEY NOT NULL, '
    'author text NOT NULL); '
    ),
    (                # fileauthor
    'CREATE TABLE IF NOT EXISTS fileauthor ('
    'fileid integer NOT NULL, '
    'aid integer NOT NULL, '
    'PRIMARY KEY(fileid, aid), '
    'FOREIGN KEY (aid) REFERENCES authors (id) on delete cascade, '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
    ),
    (                # filenotes
    'CREATE TABLE IF NOT EXISTS filenotes ('
    'fileid integer NOT NULL, '
    'id integer NOT NULL, '
    'filenote text NOT NULL, '
    'created date not null default -62135596800, '
    'modified date not null default -62135596800, '
    'PRIMARY KEY(fileid, id), '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
    ),
    (                # extensions
    'CREATE TABLE IF NOT EXISTS extensions ('
    'id integer PRIMARY KEY NOT NULL, '
    'extension text); '
    ),
)
setting_names = (     # DB settings only
    "APP_MODE",
    "AUTHOR_SEL_LIST",
    "EXT_SEL_LIST",
    "TAG_SEL_LIST",
    "DIR_CHECK",
    "SUB_DIR_CHECK",
    "TAG_CHECK",
    "IS_ALL",
    "EXT_CHECK",
    "AUTHOR_CHECK",
    "DATE_TYPE",
    "AFTER",
    "BEFORE",
    "AFTER_DATE",
    "BEFORE_DATE",
    "OPEN_CHECK",
    "OPEN_OP",
    "OPEN_VAL",
    "RATING_CHECK",
    "RATING_OP",
    "RATING_VAL",
    "LAST_SCAN_OPENED",
    "SHOW_HIDDEN",
    "DIR_HISTORY",
    "RECENT_FILES",
    "SEARCH_FILE",
    "NOTE_EDIT_STATE",
    "FILTER_FILE_ROW",
    "SELECTED_DIRS",
    "SEARCH_BY_NOTE",
)

APP_ID = 1718185071
USER_VER = 21

def check_app_schema(db_name: str) -> bool:
    with apsw.Connection(db_name) as conn:
        try:
            v = conn.cursor().execute("PRAGMA application_id").fetchone()
        except apsw.NotADBError:
            return False
    return v[0] == APP_ID

def tune_new_version() -> bool:
    conn = ag.db.conn
    try:
        v = conn.cursor().execute("PRAGMA user_version").fetchone()
        logger.info(f'{v=}')
        if v[0] != USER_VER:
            convert_to_new_version(conn, v[0])
    except apsw.SQLError as err:
        logger.exception(f'{err.args}', exc_info=True)
        return False
    return True

def convert_to_new_version(conn, old_v):
    # logger.info(f'<<<  {old_v=}, {USER_VER=}')
    if old_v == 0:
        create_tables(conn)
        return USER_VER

    if old_v < 15:
        update_to_v15(conn)
    elif old_v == 15:
        update_to_v16(conn)

    if old_v < 19:
        if not update_to_v19(conn):
            return

    if old_v < 21:
        update_to_v21(conn)

    initialize_settings(conn)
    # logger.info('>>>')

def update_to_v15(conn: apsw.Connection):
    sql1 = "alter table parentdir ADD COLUMN tool_tip text"
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    conn.cursor().execute(sql1)

def update_to_v16(conn: apsw.Connection):
    sql = """\
    update parentdir set tool_tip = null \
    from dirs d where parentdir.id = d.id \
    and parentdir.tool_tip = d.name;\
    """
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    conn.cursor().execute(sql)

def update_to_v19(conn: apsw.Connection) -> bool:
    """
    in case of duplicate files,
    link all notes to only one of the duplicate files
    with the minimum file id
    """
    hash_sql = '''
select f.hash from files f
join filenotes fn on fn.fileid=f.id
order by f.hash
'''
    id_upd ='''
update filenotes set fileid = :minid where fileid
in (select id from files where hash = :hash0);
'''
    min_id_sql = 'select min(id) from files where hash = ?'
    curs = conn.cursor().execute(hash_sql)
    hash0 = ''
    updated = False
    for hash1, *_ in curs:
        if not hash1:
            return False
        if updated and hash1 == hash0:
            continue
        if not updated and hash1 == hash0:
            min_id = conn.cursor().execute(min_id_sql, (hash0,)).fetchone()
            conn.cursor().execute(id_upd, {'minid': min_id[0], 'hash0': hash0})
            updated = True
            continue
        hash0 = hash1
        updated = False

    return True

def update_to_v21(conn: apsw.Connection):
    conn.cursor().execute(
        'ALTER TABLE parentdir RENAME COLUMN is_link TO multy;'
    )

def create_db(db_name: str) -> apsw.Connection:
    return apsw.Connection(db_name)

def create_tables(conn: apsw.Connection):
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    cursor = conn.cursor()
    for tbl in TABLES:
        cursor.execute(tbl)

    initiate_db(conn)

def initialize_settings(conn):
    sql0 = 'select key from settings'
    sql1 = 'delete from settings where key = ?'
    sql2 = 'insert or ignore into settings (key) values (:key)'

    cursor = conn.cursor()
    for key in conn.cursor().execute(sql0):
        if key not in setting_names:
            cursor.execute(sql1, key)

    for name in setting_names:
        cursor.execute(sql2, {'key': name})

    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')

def initiate_db(connection):
    sql = (
        'insert or ignore into dirs (id) values (:key)',
        'insert or ignore into dirs values (:key, :val)',
    )
    curs = connection.cursor()
    curs.execute(sql[0], {'key': 0})
    curs.execute(sql[1], {'key': 1, 'val': '@@Lost'})

    initialize_settings(connection)
