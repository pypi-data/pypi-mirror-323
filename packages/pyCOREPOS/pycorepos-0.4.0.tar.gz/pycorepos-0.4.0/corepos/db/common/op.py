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
Common schema for operational data models
"""

import sqlalchemy as sa


class EmployeeBase:
    """
    Base class for Employee models, shared by Office + Lane.
    """
    number = sa.Column('emp_no', sa.SmallInteger(), nullable=False,
                       primary_key=True, autoincrement=False)

    cashier_password = sa.Column('CashierPassword', sa.String(length=50), nullable=True)

    admin_password = sa.Column('AdminPassword', sa.String(length=50), nullable=True)

    first_name = sa.Column('FirstName', sa.String(length=255), nullable=True)

    last_name = sa.Column('LastName', sa.String(length=255), nullable=True)

    job_title = sa.Column('JobTitle', sa.String(length=255), nullable=True)

    active = sa.Column('EmpActive', sa.Boolean(), nullable=True)

    frontend_security = sa.Column('frontendsecurity', sa.SmallInteger(), nullable=True)

    backend_security = sa.Column('backendsecurity', sa.SmallInteger(), nullable=True)

    birth_date = sa.Column('birthdate', sa.DateTime(), nullable=True)

    def __str__(self):
        return ' '.join([self.first_name or '', self.last_name or '']).strip()
