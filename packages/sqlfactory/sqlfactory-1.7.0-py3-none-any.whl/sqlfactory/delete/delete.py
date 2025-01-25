"""DELETE statement builder"""

from typing import Any

from ..condition.base import ConditionBase
from ..entities import Table
from ..execute import ExecutableStatement
from ..mixins.limit import Limit, WithLimit
from ..mixins.order import OrderArg, WithOrder
from ..mixins.where import WithWhere


class Delete(ExecutableStatement, WithWhere["Delete"], WithOrder["Delete"], WithLimit["Delete"]):
    """
    DELETE statement

    >>> Delete("table", where=In("id", [1, 2, 3]))
    >>> "DELETE FROM `table` WHERE `id` IN (1,2,3)"
    """

    def __init__(
        self, table: Table | str, where: ConditionBase | None = None, order: OrderArg | None = None, limit: Limit | None = None
    ) -> None:
        """
        :param table: Table to delete from
        :param where: WHERE condition
        :param order: Ordering of matched rows, usefull when limiting number of deleted rows.
        :param limit: Limit number of deleted rows.
        """
        super().__init__(where=where, order=order, limit=limit)
        self.table = table if isinstance(table, Table) else Table(table)

    def __str__(self) -> str:
        """Construct the DELETE statement."""
        q: list[str] = [f"DELETE FROM {self.table!s}"]

        if self._where:
            q.append("WHERE")
            q.append(str(self._where))

        if self._order:
            q.append(str(self._order))

        if self._limit:
            q.append(str(self._limit))

        return " ".join(q)

    @property
    def args(self) -> list[Any]:
        """DELETE statement arguments."""
        return (
            (self._where.args if self._where else [])
            + (self._order.args if self._order else [])
            + (self._limit.args if self._limit else [])
        )


# Alias to provide better SQL compatibility
DELETE = Delete
