# -*- coding: utf-8; -*-
################################################################################
#
#  pyCOREPOS -- Python Interface to CORE POS
#  Copyright © 2018-2025 Lance Edgar
#
#  This file is part of pyCOREPOS.
#
#  pyCOREPOS is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  pyCOREPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  pyCOREPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CORE POS Transaction Data Model
"""

import sqlalchemy as sa
from sqlalchemy import orm

from corepos.db.common import trans as common


Base = orm.declarative_base()


# TODO: not sure what primary key should be for this?  am trying a
# composite one so far, we'll see...cf. also andy's comments in
# https://github.com/CORE-POS/IS4C/pull/1189#issuecomment-1597481138
class StockPurchase(Base):
    """
    Represents a member equity payment.
    """
    __tablename__ = 'stockpurchases'

    card_number = sa.Column('card_no', sa.Integer(), nullable=False, primary_key=True, autoincrement=False)

    amount = sa.Column('stockPurchase', sa.Numeric(precision=10, scale=2), nullable=True)

    datetime = sa.Column('tdate', sa.DateTime(), nullable=True, primary_key=True, autoincrement=False)

    transaction_number = sa.Column('trans_num', sa.String(length=50), nullable=True, primary_key=True)

    transaction_id = sa.Column('trans_id', sa.Integer(), nullable=True)

    department_number = sa.Column('dept', sa.Integer(), nullable=True, primary_key=True, autoincrement=False)

    def __str__(self):
        return f"#{self.card_number} for ${self.amount}"


class EquityLiveBalance(Base):

    __tablename__ = 'equity_live_balance'

    member_number = sa.Column('memnum', sa.Integer(), nullable=False, primary_key=True, autoincrement=False)

    payments = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)

    start_date = sa.Column('startdate', sa.DateTime(), nullable=True)


class DTransactionBase(common.TransactionDetailBase):
    """
    Base class for ``dtransactions`` and similar models.
    """
    store_row_id = sa.Column(sa.Integer(), primary_key=True, nullable=False)

    pos_row_id = sa.Column(sa.Integer(), nullable=True)
    store_id = sa.Column(sa.Integer(), nullable=True, default=0)
    date_time = sa.Column('datetime', sa.DateTime(), nullable=True)


class DTransaction(DTransactionBase, Base):
    """
    Data model for ``dtransactions`` table.
    """
    __tablename__ = 'dtransactions'


# TODO: deprecate / remove this
TransactionDetail = DTransaction
