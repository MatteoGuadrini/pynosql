#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# orm -- nosqlapi
#
#     Copyright (C) 2021 Matteo Guadrini <matteo.guadrini@hotmail.it>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# region Imports
from nosqlapi.kvdb.orm import Keyspace

# endregion


# region Classes
class Label(str):
    pass


class Property(dict):
    pass


class Database(Keyspace):

    def __init__(self, name, address=None, role=None, status=None, default=False):
        super().__init__(name=name)
        self.address = address
        self.role = role
        self.status = status
        self.default = default

    @property
    def online(self):
        if self.status == 'online':
            return True
        else:
            return False

# endregion
