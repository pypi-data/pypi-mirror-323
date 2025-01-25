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
Common schema for transaction data models
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr


class TransactionDetailBase:
    """
    Base class for POS transaction detail models, shared by Office +
    Lane.
    """

    # register
    register_number = sa.Column('register_no', sa.Integer(), nullable=True)

    # txn
    transaction_id = sa.Column('trans_id', sa.Integer(), nullable=True)
    transaction_number = sa.Column('trans_no', sa.Integer(), nullable=True)
    transaction_type = sa.Column('trans_type', sa.String(length=1), nullable=True)
    transaction_subtype = sa.Column('trans_subtype', sa.String(length=2), nullable=True)
    trans_status = sa.Column(sa.String(length=1), nullable=True)

    @declared_attr
    def transaction_status(self):
        return orm.synonym('trans_status')

    # cashier
    employee_number = sa.Column('emp_no', sa.Integer(), nullable=True)

    # customer
    card_number = sa.Column('card_no', sa.Integer(), nullable=True)
    member_type = sa.Column('memType', sa.Integer(), nullable=True)
    staff = sa.Column(sa.Boolean(), nullable=True)

    ##############################
    # remainder is "line item" ...
    ##############################

    upc = sa.Column(sa.String(length=13), nullable=True)

    department_number = sa.Column('department', sa.Integer(), nullable=True)

    description = sa.Column(sa.String(length=30), nullable=True)

    quantity = sa.Column(sa.Float(), nullable=True)

    scale = sa.Column(sa.Boolean(), nullable=True, default=False)

    cost = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)

    unitPrice = sa.Column('unitPrice', sa.Numeric(precision=10, scale=2), nullable=True)

    @declared_attr
    def unit_price(self):
        return orm.synonym('unitPrice')

    total = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)

    reg_price = sa.Column('regPrice', sa.Numeric(precision=10, scale=2), nullable=True)

    tax = sa.Column(sa.SmallInteger(), nullable=True)

    @declared_attr
    def tax_rate_id(self):
        return orm.synonym('tax')

    food_stamp = sa.Column('foodstamp', sa.Boolean(), nullable=True)

    discount = sa.Column(sa.Numeric(precision=10, scale=2), nullable=True)

    member_discount = sa.Column('memDiscount', sa.Numeric(precision=10, scale=2), nullable=True)

    discountable = sa.Column(sa.Boolean(), nullable=True)

    discount_type = sa.Column('discounttype', sa.Integer(), nullable=True)

    voided = sa.Column(sa.Integer(), nullable=True)

    percent_discount = sa.Column('percentDiscount', sa.Integer(), nullable=True)

    item_quantity = sa.Column('ItemQtty', sa.Float(), nullable=True)

    volume_discount_type = sa.Column('volDiscType', sa.Integer(), nullable=True)

    volume = sa.Column(sa.Integer(), nullable=True)

    volume_special = sa.Column('VolSpecial', sa.Numeric(precision=10, scale=2), nullable=True)

    mix_match = sa.Column('mixMatch', sa.String(length=13), nullable=True)

    matched = sa.Column(sa.Boolean(), nullable=True)

    num_flag = sa.Column('numflag', sa.Integer(), nullable=True, default=0)

    char_flag = sa.Column('charflag', sa.String(length=2), nullable=True)

    def __str__(self):
        return self.description or ''
