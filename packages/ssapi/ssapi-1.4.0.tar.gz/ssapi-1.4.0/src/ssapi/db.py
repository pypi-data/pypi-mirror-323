import json
import typing as T
import uuid

from ssapi.auth import UserSession
from ssapi.types import Undefined
from ssapi.entities import Sale, Return, Transaction
from ssapi.relational import Database
from ssapi.db_utils import (
    create_date_where_clause,
    create_shop_where_clause,
    WhereClause,
)


class ShopDatabase(Database):
    """A database that stores data about shops"""

    def _tables_init(self) -> None:
        """Initialize the tables"""
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS sales"
            "("
            "id INTEGER PRIMARY KEY,"
            "product CHAR, "
            "shop CHAR, "
            "quantity INT, "
            "date DATE DEFAULT CURRENT_TIMESTAMP, "
            "is_discounted BOOLEAN"
            ")"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS returns"
            "("
            "id INTEGER PRIMARY KEY,"
            "product CHAR, "
            "shop CHAR, "
            "quantity INT, "
            "date DATE DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS settings"
            "("
            "owner CHAR PRIMARY KEY,"
            "data CHAR"
            ")"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS user_sessions"
            "("
            "id INTEGER PRIMARY KEY,"
            "secret CHAR,"
            "datetime DATETIME DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

    def add_sales(self, *sales: Sale) -> int:
        """Record sale transactions and return the number of rows created"""
        cur = self.conn.executemany(
            "INSERT INTO sales VALUES(?, ?, ?, ?, ?, ?)",
            (sale.as_tuple() for sale in sales),
        )
        self.conn.commit()
        return cur.rowcount

    def add_returns(self, *returns: Return) -> int:
        """Record sale transactions and return the number of rows created"""
        cur = self.conn.executemany(
            "INSERT INTO returns VALUES(?, ?, ?, ?, ?)",
            (ret.as_tuple() for ret in returns),
        )
        self.conn.commit()
        return cur.rowcount

    def get_shops(self) -> T.Generator[str, None, None]:
        """Get all the shops"""
        cur = self.conn.execute("SELECT DISTINCT shop FROM sales")
        for shop, *_ in cur.fetchall():
            yield shop

    def get_sales(
        self,
        date_start="",
        date_end="",
        is_discounted=Undefined(),
        shop="",
    ) -> T.Generator[Sale, None, None]:
        """Get the sales according to the given criteria"""
        where = create_date_where_clause(date_start, date_end)
        where = where.AND(create_shop_where_clause(shop))
        where = where.AND(WhereClause.create(is_discounted=is_discounted))
        cur = self.conn.execute(
            f"SELECT * FROM sales {where.clause}", where.values
        )
        for result in cur.fetchall():
            yield Sale(*result)

    def get_returns(
        self,
        date_start="",
        date_end="",
        shop="",
    ) -> T.Generator[Return, None, None]:
        """Get the sales according to the given criteria"""
        where = create_date_where_clause(date_start, date_end)
        where = where.AND(create_shop_where_clause(shop))
        cur = self.conn.execute(
            f"SELECT * FROM returns {where.clause}", where.values
        )
        for result in cur.fetchall():
            yield Return(*result)

    def _get_transaction(
        self, transaction_type: T.Type[Transaction], id: int
    ) -> T.Optional[Transaction]:
        """Get a transaction by Id"""
        stmt = f"SELECT * FROM {transaction_type.Meta.table_name} WHERE id=?"
        cur = self.conn.execute(stmt, (id,))
        if result := cur.fetchone():
            return transaction_type(*result)
        else:
            return None

    def get_sale(self, id: int) -> T.Optional[Sale]:
        """Get a specific sale by its id"""
        return self._get_transaction(Sale, id)

    def put_sale(self, id: int, sale: Sale) -> T.Optional[Sale]:
        """Get a specific sale by its id"""
        stmt = "REPLACE INTO sales VALUES(?, ?, ?, ?, ?, ?)"
        self.conn.execute(stmt, sale.as_tuple())

    def put_return(self, id: int, return_: Return) -> T.Optional[Sale]:
        """Get a specific sale by its id"""
        stmt = "REPLACE INTO returns VALUES(?, ?, ?, ?, ?)"
        self.conn.execute(stmt, return_.as_tuple())

    def get_return(self, id: int) -> T.Optional[Return]:
        """Get a specific sale by its id"""
        return self._get_transaction(Return, id)

    def get_products(self) -> T.Generator[tuple, None, None]:
        cur = self.conn.execute("SELECT DISTINCT product FROM sales")
        for item in cur.fetchall():
            yield item[0]

    def put_settings(self, owner: str, data: dict) -> None:
        self.conn.execute(
            "REPLACE INTO settings VALUES(?, ?)", (owner, json.dumps(data))
        )
        self.conn.commit()

    def get_settings(self, owner: str) -> T.Optional[dict]:
        cur = self.conn.execute(
            "SELECT data FROM settings WHERE owner=?", (owner,)
        )
        data = cur.fetchone()
        return None if data is None else json.loads(data[0])

    def delete_sessions(self):
        self.conn.execute("DELETE FROM user_sessions")
        self.conn.commit()

    def create_session(self) -> UserSession:
        self.delete_sessions()
        secret = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO user_sessions(secret) VALUES(?)", (secret,)
        )
        self.conn.commit()
        return UserSession(None, secret, None)

    def get_current_session(self) -> UserSession:
        cur = self.conn.execute(
            "SELECT * FROM user_sessions"
            " WHERE datetime = (SELECT MAX(datetime) FROM user_sessions)"
        )
        data = cur.fetchone()
        if data is None:
            return UserSession(None, None, None)
        else:
            return UserSession(*data)
