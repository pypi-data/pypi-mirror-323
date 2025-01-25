# -*- coding: utf-8 -*-
import heimdall
import os as _os
import re as _re
from sys import version_info as _py
from urllib.parse import urlparse
from ..decorators import get_database, create_database
_python_version = (_py.major, _py.minor) >= (3, 8)
try:
    from mariadb import connect
    _installed = True
except ModuleNotFoundError:  # pragma: no cover
    _installed = False
except SyntaxError:  # pragma: no cover
    _python_version = False
LENGTH_PREFIX = 'len:'


def check_available():
    if not _python_version:
        version = '.'.join(str(n) for n in _py[:3])
        message = f"Python 3.8 or later required (found: {version})."
        raise ModuleNotFoundError(message)
    if not _installed:
        message = "Module 'mariadb' required."
        raise ModuleNotFoundError(message)
    return _installed and _python_version


@get_database(['sql:mariadb', ])
def getDatabase(**options):
    r"""Loads a MariaDB database as a HERA elements tree

    :param \**options: Keyword arguments, see below.
    :Keyword arguments:
        * **url** (``str``) -- URL of the database to load
        * **entities** (``list``) -- List of tables to load;
          empty list will do nothing

    Regarding SQL to HERA transformation, the following apply:

    * Each of the SQL table name in the ``entities`` option
      will be loaded as a single HERA entity.
    * Each column of a table will be loaded as a single HERA
      attribute, referencing a single HERA property.
      This means that, for example, two tables with the same
      ``id`` primary key column will become two different
      attribues, referencing two different properties.
      These properties can then be factorized using pyHeimdall.
      See :py:class:`heimdall.util.merge_properties` module for details.
    """
    check_available()  # breaks if not
    connection = _connect(options['url'])
    with connection.cursor() as cursor:
        hera = _create_tree(options['entities'], cursor)
    connection.close()
    return hera


def _connect(url):
    url = urlparse(url)
    # due to urlparse, url.path is something like '/dbname'
    # but mariadb.connect wants database = 'dbname'
    connection = connect(database=url.path.split('/')[1],
                         user=url.username, password=url.password,
                         host=url.hostname, port=url.port)
    # TBD: can connection.is_connected() be False here?
    return connection


def _create_tree(tables, cursor):
    root = heimdall.util.tree.create_empty_tree()
    properties = root.get_container('properties')
    entities = root.get_container('entities')
    items = root.get_container('items')
    for table in tables:
        # create entity for this table
        entity, aid_vs_property = _create_entity(table, cursor)
        entities.append(entity)
        # create properties for this entity
        for p in aid_vs_property.values():
            properties.append(p)
        # create items for this entity
        eid = entity.get('id')
        result = cursor.execute(f'SELECT * FROM {table}')
        for row in cursor.fetchall():
            items.append(_create_item(eid, row, aid_vs_property))
    return root


def _create_item(eid, row, aid_vs_property):
    item = heimdall.elements.Item(eid=eid)
    for index, (aid, p) in enumerate(aid_vs_property.items()):
        value = row[index]
        if value is None:
            continue
        item.append(_create_metadata(value, aid=aid, pid=p.get('id')))
    return item


def _create_metadata(value, pid=None, aid=None):
    metadata = heimdall.elements.Metadata()
    if aid is not None:
        metadata.set('aid', aid)
    if pid is not None:
        metadata.set('pid', pid)
    metadata.text = str(value)
    return metadata


def _create_entity(table, cursor):
    cursor.execute(f'SHOW CREATE TABLE {table}')
    create_table_query = cursor.fetchall()[0][1]
    entity = heimdall.elements.Entity(id=table)
    entity.name = [table, ]
    comment = _get_table_comment(create_table_query)
    if comment is not None:
        entity.description = [comment, ]
    pointers = _get_pointers(table, cursor)
    aid_vs_property = dict()
    cursor.execute(f'SHOW FULL COLUMNS FROM {table}')
    for row in cursor.fetchall():
        a = _create_attribute(row, table, pointers)
        a.entity = entity
        entity.append(a)
        aid_vs_property[a.get('id')] = _create_property(table, row)
    return entity, aid_vs_property


def _get_table_comment(create_table_query):
    pattern = _re.compile(r"COMMENT='(?P<res>[\w\s]*)'")
    m = pattern.search(create_table_query)
    return m.group('res') if m is not None else None


def _get_pointers(source_table, cursor):
    """Gets pointer attributes for ``source_table``

    Each foreign key in ``source_table`` in SQL is a pointer in HERA.
    For example if ``SHOW CREATE TABLE source_table`` returns something such as
    ``FOREIGN KEY (`source_attr`) REFERENCES `target_table` (`target_attr`)``,
    then the attribute ``source_attr`` of entity ``source_table`` is a pointer
    to the content of attribute ``target_attr`` of entity ``target_table``.
    """
    cursor.execute(f'SHOW CREATE TABLE {source_table}')
    parts = cursor.fetchall()
    assert len(parts) == 1
    assert len(parts[0]) == 2
    assert parts[0][0] == source_table
    haystack = parts[0][1]
    needle = _re.compile(r"FOREIGN KEY \(`(?P<source_attr>\w+)`\) REFERENCES `(?P<target_table>\w+)` \(`(?P<target_attr>\w+)`\)", _re.IGNORECASE)  # nopep8: E501
    groups = needle.findall(haystack)
    pointers = dict()
    for match in groups:
        source_attr = f'{match[0]}_attr'
        target_table = match[1]
        target_attr = f'{match[2]}_attr'
        pointers[source_attr] = f'@{target_table}.{target_attr}'
    return pointers


def _create_attribute(row, table, pointers=None):
    name = row[0]
    sqltype = row[1]
    collation = row[2]
    nullability = row[3]  # YES|NO
    indexed = row[4]  # PRI|UNI|MUL
    default_value = row[5]
    extra = row[6]
    privileges = row[7]
    comment = row[8]
    root = heimdall.elements.Attribute(**{
        'id': f'{table}.{name}_attr', 'pid': f'{table}.{name}',
        'min': str(0) if nullability == 'YES' else str(1),
        'max': str(1),  # TODO hera allows repeatability, sql does not (as is)
        })
    pointers = pointers or dict()
    pointer_type = pointers.get(f'{name}_attr', None)
    if pointer_type is not None:
        root.type = pointer_type
    else:
        root.type = _type_sql2hera(sqltype)
    root.name = [name, ]
    if comment:
        root.description = [comment, ]
    return root


def _create_property(table, row):
    name = row[0]
    sqltype = row[1]
    comment = row[8]
    root = heimdall.elements.Property(id=f'{table}.{name}')
    root.type = _type_sql2hera(sqltype)
    root.name = [name, ]
    if comment is not None:
        root.description = [comment, ]
    return root


def _type_sql2hera(sqltype):
    # NOTE: the following lines might allow python3.7 support
    # if type(sqltype) == bytes:
    #     try:
    #         import chardet  # happens with python3.7 or lower
    #         encoding = chardet.detect(sqltype)['encoding']
    #     except ModuleNotFoundError:
    #         encoding = 'ascii'
    #     sqltype = sqltype.decode(encoding)
    if (sqltype == 'date' or
            sqltype == 'datetime' or
            sqltype == 'timestamp'):
        return 'datetime'
    if (sqltype.startswith('varchar') or
            sqltype.startswith('char') or
            sqltype.startswith('tinytext')):
        return 'text'
    if (sqltype.startswith('int') or
            sqltype.startswith('tinyint')):
        return 'number'
    raise ValueError(f"Unknown type '{sqltype}'")


__version__ = '1.0.0'
__all__ = ['getDatabase', '__version__']
__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
