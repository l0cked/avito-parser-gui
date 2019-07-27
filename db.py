import aiosqlite


class Db:
    async def db_init(self):
        self.db = await aiosqlite.connect('avito-parser-gui.db')
        await self.db_create()

    async def db_close(self):
        await self.db.close()

    async def db_create(self):
        await self.db.executescript('''

            CREATE TABLE IF NOT EXISTS log (
            id integer primary key autoincrement not null,
            added datetime default (datetime('now', 'localtime')),
            message text not null,
            messageType text not null,
            messageData text not null);

            CREATE TABLE IF NOT EXISTS proxy (
            id integer primary key autoincrement not null,
            added datetime default (datetime('now', 'localtime')),
            country text not null,
            host text not null,
            port text not null,
            url text not null unique,
            response_time real not null,
            used integer not null default 0,
            error integer not null default 0);

            CREATE TABLE IF NOT EXISTS items (
            id integer primary key autoincrement not null,
            added datetime default (datetime('now', 'localtime')),
            dt datetime not null,
            url text not null unique,
            name text not null,
            price text not null,
            desc text not null,
            author text not null,
            address text not null,
            phone text not null);

            ''')
        await self.db.commit()
