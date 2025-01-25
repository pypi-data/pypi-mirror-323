from typing import Any, Generic, Iterable, Optional, Sequence, Tuple, TypeVar

from clickhouse_driver import Client
from clickhouse_driver.errors import Error

# Define a type variable for the result type
T = TypeVar("T")


class Connection:
    def __init__(self, dsn: str, **kwargs):
        self.client = Client(dsn=dsn, **kwargs)
        self.closed = False
        self.dsn = dsn

    def close(self):
        """Close the connection."""
        self.client.disconnect()
        self.closed = True

    def commit(self):
        """Commit the current transaction."""

    def cursor(self):
        """Return a Cursor object for executing queries."""

    def rollback(self):
        """Roll back the current transaction."""


class BaseCursor(Generic[T]):
    result: Iterable[T]

    def __init__(self, connection: Connection):
        """Create a cursor for executing queries."""
        self.connection = connection
        self.client = connection.client
        self.arraysize = 1

    def __iter__(self):
        """Allow iteration over the cursor to fetch rows."""
        if hasattr(self, "result"):
            self.result_iter = iter(self.result)
        else:
            self.result_iter = iter([])
        return self

    def close(self):
        """Close the cursor."""
        self.result = None
        self.result_iter = None

    def execute(self, operation: str, parameters: Optional[dict[str, Any]] = None):
        """Execute a SQL query with optional parameters."""
        try:
            if parameters:
                self.result = self.client.execute(operation, parameters)
            else:
                self.result = self.client.execute(operation)
        except Error as e:
            raise RuntimeError(f"ClickHouse query error: {e}")

    def executemany(self, sql: str, seq_of_params: Sequence[dict[str, Any]]):
        """Execute a query for multiple parameter sets."""

    def fetchone(self) -> Optional[T]:
        """Fetch a single row."""
        raise NotImplementedError

    def fetchmany(self, size: int) -> list[T]:
        """Fetch multiple rows."""
        raise NotImplementedError

    def fetchall(self) -> list[T]:
        """Fetch all rows."""
        raise NotImplementedError

    def setinputsizes(self, sizes):
        """This is a no-op method included for PEP 249 compliance."""

    def setoutputsize(self, size, column=None):
        """This is a no-op method included for PEP 249 compliance."""


class TupleCursor(BaseCursor[Tuple]):
    def fetchone(self) -> Optional[Tuple]:
        try:
            return next(self.result_iter)
        except (StopIteration, AttributeError):
            return None

    def fetchmany(self, size=None) -> list[Tuple]:
        size = size or self.arraysize
        result = []
        for _ in range(size):
            row = self.fetchone()
            if row is None:
                break
            result.append(row)
        return result

    def fetchall(self) -> list[Tuple]:
        return list(self.result_iter)


class DictCursor(BaseCursor[dict[str, Any]]):
    def fetchone(self) -> Optional[dict[str, Any]]:
        rv = super(DictCursor, self).fetchone()
        return None if rv is None else dict(zip(self._columns, rv))

    def fetchmany(self, size: int) -> list[dict[str, Any]]:
        rv = super(DictCursor, self).fetchmany(size=size)
        return [] if rv is None else [dict(zip(self._columns, x)) for x in rv]

    def fetchall(self) -> list[dict[str, Any]]:
        rv = super(DictCursor, self).fetchall()
        return [dict(zip(self._columns, x)) for x in rv]
