#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# core -- nosqlapi
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

from typing import Any, Union

class Batch:

    def __init__(self, session: Session, batch: str):
        self._session: Session
        self._query: str

    def execute(self, *args, **kwargs) -> Union[Any, Response]: ...

class Connection:

    def close(self, *args, **kwargs) -> None: ...

    def connect(self, *args, **kwargs) -> Session: ...

    def create_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def has_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def databases(self, *args, **kwargs) -> Union[list, Response]: ...

    def show_database(self, *args, **kwargs) -> Union[Any, Response]: ...


class Selector:

    def build(self, *args, **kwargs) -> str: ...

class Session:

    def get(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def insert(self, *args, **kwargs) -> Union[bool, Response]: ...

    def insert_many(self, *args, **kwargs) -> Union[bool, Response]: ...

    def update(self, *args, **kwargs) -> Union[bool, Response]: ...

    def update_many(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete(self, *args, **kwargs) -> Union[bool, Response]: ...

    def close(self, *args, **kwargs) -> None: ...

    def find(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def grant(self, *args, **kwargs) -> Union[Any, Response]: ...

    def revoke(self, *args, **kwargs) -> Union[Any, Response]: ...

    def new_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def set_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def add_index(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_index(self, *args, **kwargs) -> Union[bool, Response]: ...

    @staticmethod
    def call(batch: Batch, *args, **kwargs) -> Union[Any, Response]: ...

class Response:...
