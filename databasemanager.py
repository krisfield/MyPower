import sqlite3

class DatabaseManager(object):
  def __init__(self, db):
    self.conn = sqlite3.connect(db)
    self.conn.execute('pragma foreign_keys = on')
    self.conn.commit()
    self.cur = self.conn.cursor()

  def query(self, query, args=''):
    self.cur.execute(query, args)
    self.conn.commit()
    return self.cur

  def querymany(self, arg, arg2):
    self.cur.executemany(arg, arg2)
    self.conn.commit()
    return self.cur

  def fetchall(self):
    return self.cur.fetchall()

  def fetchone(self):
    return self.cur.fetchone()

  def __del__(self):
    self.conn.close()
