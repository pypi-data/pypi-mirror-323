"""Simple binary comparison conditions."""

from typing import Any

from ..statement import Statement
from .base import Condition, StatementOrColumn


class SimpleCondition(Condition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    Simple condition comparing one column with given value, using specified operator.
    """

    def __init__(self, column: StatementOrColumn, operator: str, value: Statement | Any) -> None:
        # pylint: disable=duplicate-code   # It does not make sense to generalize two-row statement used on two places.
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param operator: Operator to use for comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        if not isinstance(column, Statement):
            # pylint: disable=import-outside-toplevel,cyclic-import
            from ..entities import Column

            column = Column(column)

        args = []

        if isinstance(column, Statement):
            args.extend(column.args)

        if isinstance(value, Statement):
            args.extend(value.args)

        elif not isinstance(value, Statement):
            args.append(value)

        if isinstance(value, Statement):
            super().__init__(f"{column!s} {operator} {value!s}", *args)
        else:
            super().__init__(f"{column!s} {operator} %s", *args)


class Equals(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` = <value>
    - `column` IS NULL
    - <statement> = <value>
    - <statement> IS NULL
    """

    def __init__(self, column: StatementOrColumn, value: Any | None | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        if value is None:
            super().__init__(column, "IS", value)
        else:
            super().__init__(column, "=", value)


class NotEquals(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` != <value>
    - <statement> != <value>
    - `column` IS NOT NULL
    - <statement> IS NOT NULL
    """

    def __init__(self, column: StatementOrColumn, value: Any | None | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        if value is None:
            super().__init__(column, "IS NOT", value)
        else:
            super().__init__(column, "!=", value)


class GreaterThanOrEquals(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` >= <value>
    - <statement> >= <value>
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, ">=", value)


class GreaterThan(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` > <value>
    - <statement> > <value>
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, ">", value)


class LessThanOrEquals(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` <= <value>
    - <statement> <= <value>
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, "<=", value)


class LessThan(SimpleCondition):
    # pylint: disable=too-few-public-methods  # As everything is handled in base classes.
    """
    - `column` < <value>
    - <statement> < <value>
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, "<", value)


# Convenient aliases for shorter code.
Eq = Equals
Ge = GreaterThanOrEquals
Gt = GreaterThan
Le = LessThanOrEquals
Lt = LessThan
Ne = NotEquals
