"""BETWEEN condition generator"""

from typing import Any

from ..entities import Column
from ..statement import Statement
from .base import Condition, StatementOrColumn


# pylint: disable=too-few-public-methods  # As everything is handled by base classes.
class Between(Condition):
    # pylint: disable=duplicate-code  # It does not make sense to generalize two-row statement used on two places.
    """
    Provides generation for following syntax:

    - `column` BETWEEN <lower_bound> AND <upper_bound>
    - `column` NOT BETWEEN <lower_bound> AND <upper_bound>
    - <statement> BETWEEN <lower_bound> AND <upper_bound>
    - <statement> NOT BETWEEN <lower_bound> AND <upper_bound>

    """

    def __init__(
        self, column: StatementOrColumn, lower_bound: Any | Statement, upper_bound: Any | Statement, *, negative: bool = False
    ) -> None:
        lower_bound_s = "%s"
        upper_bound_s = "%s"

        if not isinstance(column, Statement):
            column = Column(column)

        args = []

        if isinstance(column, Statement):
            args.extend(column.args)

        if isinstance(lower_bound, Statement):
            lower_bound_s = str(lower_bound)
            if isinstance(lower_bound, Statement):
                args.extend(lower_bound.args)
        else:
            args.append(lower_bound)

        if isinstance(upper_bound, Statement):
            upper_bound_s = str(upper_bound)
            if isinstance(upper_bound, Statement):
                args.extend(upper_bound.args)
        else:
            args.append(upper_bound)

        super().__init__(f"{column!s} {'NOT ' if negative else ''}BETWEEN {lower_bound_s} AND {upper_bound_s}", *args)
