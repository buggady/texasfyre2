/* cursor.c - the cursor type
 *
 * Copyright (C) 2004-2015 Gerhard H�ring <gh@ghaering.de>
 *
 * This file is part of pysqlite.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty.  In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 */

#include "cursor.h"
#include "module.h"
#include "util.h"

/* used to decide wether to call PyInt_FromLong or PyLong_FromLongLong */
#ifndef INT32_MIN
#define INT32_MIN (-2147483647 - 1)
#endif
#ifndef INT32_MAX
#define INT32_MAX 2147483647
#endif

PyObject* pysqlite_cursor_iternext(pysqlite_Cursor* self);

static char* errmsg_fetch_across_rollback = "Cursor needed to be reset because of commit/rollback and can no longer be fetched from.";

static int pysqlite_cursor_init(pysqlite_Cursor* self, PyObject* args, PyObject* kwargs)
{
    pysqlite_Connection* connection;

    if (!PyArg_ParseTuple(args, "O!", &pysqlite_ConnectionType, &connection))
    {
        return -1;
    }

    Py_INCREF(connection);
    self->connection = connection;
    self->statement = NULL;
    self->next_row = NULL;
    self->in_weakreflist = NULL;

    self->row_cast_map = PyList_New(0);
    if (!self->row_cast_map) {
        return -1;
    }

    Py_INCREF(Py_None);
    self->description = Py_None;

    Py_INCREF(Py_None);
    self->lastrowid= Py_None;

    self->arraysize = 1;
    self->closed = 0;
    self->reset = 0;

    self->rowcount = -1L;

    if (!pysqlite_check_thread(self->connection)) {
        return -1;
    }

    if (!pysqlite_connection_register_cursor(connection, (PyObject*)self)) {
        return -1;
    }

    self->initialized = 1;

    return 0;
}

static void pysqlite_cursor_dealloc(pysqlite_Cursor* self)
{
    /* Reset the statement if the user has not closed the cursor */
    if (self->statement) {
        (void)pysqlite_statement_reset(self->statement);
        Py_DECREF(self->statement);
    }

    Py_XDECREF(self->connection);
    Py_XDECREF(self->row_cast_map);
    Py_XDECREF(self->description);
    Py_XDECREF(self->lastrowid);
    Py_XDECREF(self->next_row);

    if (self->in_weakreflist != NULL) {
        PyObject_ClearWeakRefs((PyObject*)self);
    }

    self->ob_type->tp_free((PyObject*)self);
}

PyObject* _pysqlite_get_converter(PyObject* key)
{
    PyObject* upcase_key;
    PyObject* retval;

    upcase_key = PyObject_CallMethod(key, "upper", "");
    if (!upcase_key) {
        return NULL;
    }

    retval = PyDict_GetItem(converters, upcase_key);
    Py_DECREF(upcase_key);

    return retval;
}

int pysqlite_build_row_cast_map(pysqlite_Cursor* self)
{
    int i;
    const char* type_start = (const char*)-1;
    const char* pos;

    const char* colname;
    const char* decltype;
    PyObject* py_decltype;
    PyObject* converter;
    PyObject* key;

    if (!self->connection->detect_types) {
        return 0;
    }

    Py_XDECREF(self->row_cast_map);
    self->row_cast_map = PyList_New(0);

    for (i = 0; i < sqlite3_column_count(self->statement->st); i++) {
        converter = NULL;

        if (self->connection->detect_types & PARSE_COLNAMES) {
            colname = sqlite3_column_name(self->statement->st, i);
            if (colname) {
                for (pos = colname; *pos != 0; pos++) {
                    if (*pos == '[') {
                        type_start = pos + 1;
                    } else if (*pos == ']' && type_start != (const char*)-1) {
                        key = PyString_FromStringAndSize(type_start, pos - type_start);
                        if (!key) {
                            /* creating a string failed, but it is too complicated
                             * to propagate the error here, we just assume there is
                             * no converter and proceed */
                            break;
                        }

                        converter = _pysqlite_get_converter(key);
                        Py_DECREF(key);
                        break;
                    }
                }
            }
        }

        if (!converter && self->connection->detect_types & PARSE_DECLTYPES) {
            decltype = sqlite3_column_decltype(self->statement->st, i);
            if (decltype) {
                for (pos = decltype;;pos++) {
                    /* Converter names are split at '(' and blanks.
                     * This allows 'INTEGER NOT NULL' to be treated as 'INTEGER' and
                     * 'NUMBER(10)' to be treated as 'NUMBER', for example.
                     * In other words, it will work as people expect it to work.*/
                    if (*pos == ' ' || *pos == '(' || *pos == 0) {
                        py_decltype = PyString_FromStringAndSize(decltype, pos - decltype);
                        if (!py_decltype) {
                            return -1;
                        }
                        break;
                    }
                }

                converter = _pysqlite_get_converter(py_decltype);
                Py_DECREF(py_decltype);
            }
        }

        if (!converter) {
            converter = Py_None;
        }

        if (PyList_Append(self->row_cast_map, converter) != 0) {
            if (converter != Py_None) {
                Py_DECREF(converter);
            }
            Py_CLEAR(self->row_cast_map);

            return -1;
        }
    }

    return 0;
}

PyObject* _pysqlite_build_column_name(const char* colname)
{
    const char* pos;

    if (!colname) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    for (pos = colname;; pos++) {
        if (*pos == 0 || *pos == '[') {
            if ((*pos == '[') && (pos > colname) && (*(pos-1) == ' ')) {
                pos--;
            }
            return PyString_FromStringAndSize(colname, pos - colname);
        }
    }
}

static PyObject* pysqlite_unicode_from_string(const char* val_str, Py_ssize_t size, int optimize)
{
    const char* check;
    Py_ssize_t pos;
    int is_ascii = 0;

    if (optimize) {
        is_ascii = 1;

        check = val_str;
        for (pos = 0; pos < size; pos++) {
            if (*check & 0x80) {
                is_ascii = 0;
                break;
            }

            check++;
        }
    }

    if (is_ascii) {
        return PyString_FromStringAndSize(val_str, size);
    } else {
        return PyUnicode_DecodeUTF8(val_str, size, NULL);
    }
}

/*
 * Returns a row from the currently active SQLite statement
 *
 * Precondidition:
 * - sqlite3_step() has been called before and it returned SQLITE_ROW.
 */
PyObject* _pysqlite_fetch_one_row(pysqlite_Cursor* self)
{
    int i, numcols;
    PyObject* row;
    PyObject* item = NULL;
    int coltype;
    PyObject* converter;
    PyObject* converted;
    Py_ssize_t nbytes;
    PyObject* buffer;
    void* raw_buffer;
    const char* val_str;
    char buf[200];
    const char* colname;

    if (self->reset) {
        PyErr_SetString(pysqlite_InterfaceError, errmsg_fetch_across_rollback);
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    numcols = sqlite3_data_count(self->statement->st);
    Py_END_ALLOW_THREADS

    row = PyTuple_New(numcols);
    if (!row) {
        return NULL;
    }

    for (i = 0; i < numcols; i++) {
        if (self->connection->detect_types) {
            converter = PyList_GetItem(self->row_cast_map, i);
            if (!converter) {
                converter = Py_None;
            }
        } else {
            converter = Py_None;
        }

        if (converter != Py_None) {
            nbytes = sqlite3_column_bytes(self->statement->st, i);
            val_str = (const char*)sqlite3_column_blob(self->statement->st, i);
            if (!val_str) {
                Py_INCREF(Py_None);
                converted = Py_None;
            } else {
                item = PyString_FromStringAndSize(val_str, nbytes);
                if (!item) {
                    return NULL;
                }
                converted = PyObject_CallFunction(converter, "O", item);
                Py_DECREF(item);
                if (!converted) {
                    break;
                }
            }
        } else {
            Py_BEGIN_ALLOW_THREADS
            coltype = sqlite3_column_type(self->statement->st, i);
            Py_END_ALLOW_THREADS
            if (coltype == SQLITE_NULL) {
                Py_INCREF(Py_None);
                converted = Py_None;
            } else if (coltype == SQLITE_INTEGER) {
                converted = _pysqlite_long_from_int64(sqlite3_column_int64(self->statement->st, i));
            } else if (coltype == SQLITE_FLOAT) {
                converted = PyFloat_FromDouble(sqlite3_column_double(self->statement->st, i));
            } else if (coltype == SQLITE_TEXT) {
                val_str = (const char*)sqlite3_column_text(self->statement->st, i);
                nbytes = sqlite3_column_bytes(self->statement->st, i);
                if ((self->connection->text_factory == (PyObject*)&PyUnicode_Type)
                    || (self->connection->text_factory == pysqlite_OptimizedUnicode)) {

                    converted = pysqlite_unicode_from_string(val_str, nbytes,
                        self->connection->text_factory == pysqlite_OptimizedUnicode ? 1 : 0);

                    if (!converted) {
                        colname = sqlite3_column_name(self->statement->st, i);
                        if (!colname) {
                            colname = "<unknown column name>";
                        }
                        PyOS_snprintf(buf, sizeof(buf) - 1, "Could not decode to UTF-8 column '%s' with text '%s'",
                                     colname , val_str);
                        PyErr_SetString(pysqlite_OperationalError, buf);
                    }
                } else if (self->connection->text_factory == (PyObject*)&PyString_Type) {
                    converted = PyString_FromStringAndSize(val_str, nbytes);
                } else {
                    converted = PyObject_CallFunction(self->connection->text_factory, "s#", val_str, nbytes);
                }
            } else {
                /* coltype == SQLITE_BLOB */
                nbytes = sqlite3_column_bytes(self->statement->st, i);
                buffer = PyBuffer_New(nbytes);
                if (!buffer) {
                    break;
                }
                if (PyObject_AsWriteBuffer(buffer, &raw_buffer, &nbytes)) {
                    break;
                }
                memcpy(raw_buffer, sqlite3_column_blob(self->statement->st, i), nbytes);
                converted = buffer;
            }
        }

        if (converted) {
            PyTuple_SetItem(row, i, converted);
        } else {
            Py_INCREF(Py_None);
            PyTuple_SetItem(row, i, Py_None);
        }
    }

    if (PyErr_Occurred()) {
        Py_DECREF(row);
        row = NULL;
    }

    return row;
}

/*
 * Checks if a cursor object is usable.
 *
 * 0 => error; 1 => ok
 */
static int check_cursor(pysqlite_Cursor* cur)
{
    if (!cur->initialized) {
        PyErr_SetString(pysqlite_ProgrammingError, "Base Cursor.__init__ not called.");
        return 0;
    }

    if (cur->closed) {
        PyErr_SetString(pysqlite_ProgrammingError, "Cannot operate on a closed cursor.");
        return 0;
    }

    if (cur->locked) {
        PyErr_SetString(pysqlite_ProgrammingError, "Recursive use of cursors not allowed.");
        return 0;
    }

    return pysqlite_check_thread(cur->connection) && pysqlite_check_connection(cur->connection);
}

PyObject* _pysqlite_query_execute(pysqlite_Cursor* self, int multiple, PyObject* args)
{
    PyObject* operation = NULL;
    PyObject* parameters_list = NULL;
    PyObject* parameters_iter = NULL;
    PyObject* parameters = NULL;
    int i;
    int rc;
    PyObject* func_args = NULL;
    PyObject* result = NULL;
    int numcols;
    PyObject* descriptor = NULL;
    PyObject* second_argument = NULL;
    int allow_8bit_chars;

    if (!check_cursor(self)) {
        goto error;
    }

    self->locked = 1;
    self->reset = 0;

    /* Make shooting yourself in the foot with not utf-8 decodable 8-bit-strings harder */
    allow_8bit_chars = ((self->connection->text_factory != (PyObject*)&PyUnicode_Type) &&
        (self->connection->text_factory != pysqlite_OptimizedUnicode));

    Py_CLEAR(self->next_row);

    if (multiple) {
        /* executemany() */
        if (!PyArg_ParseTuple(args, "OO", &operation, &second_argument)) {
            goto error;
        }

        if (!PyString_Check(operation) && !PyUnicode_Check(operation)) {
            PyErr_SetString(PyExc_ValueError, "operation parameter must be str or unicode");
            goto error;
        }

        if (PyIter_Check(second_argument)) {
            /* iterator */
            Py_INCREF(second_argument);
            parameters_iter = second_argument;
        } else {
            /* sequence */
            parameters_iter = PyObject_GetIter(second_argument);
            if (!parameters_iter) {
                goto error;
            }
        }
    } else {
        /* execute() */
        if (!PyArg_ParseTuple(args, "O|O", &operation, &second_argument)) {
            goto error;
        }

        if (!PyString_Check(operation) && !PyUnicode_Check(operation)) {
            PyErr_SetString(PyExc_ValueError, "operation parameter must be str or unicode");
            goto error;
        }

        parameters_list = PyList_New(0);
        if (!parameters_list) {
            goto error;
        }

        if (second_argument == NULL) {
            second_argument = PyTuple_New(0);
            if (!second_argument) {
                goto error;
            }
        } else {
            Py_INCREF(second_argument);
        }
        if (PyList_Append(parameters_list, second_argument) != 0) {
            Py_DECREF(second_argument);
            goto error;
        }
        Py_DECREF(second_argument);

        parameters_iter = PyObject_GetIter(parameters_list);
        if (!parameters_iter) {
            goto error;
        }
    }

    if (self->statement != NULL) {
        /* There is an active statement */
        rc = pysqlite_statement_reset(self->statement);
    }

    /* reset description and rowcount */
    Py_DECREF(self->description);
    Py_INCREF(Py_None);
    self->description = Py_None;
    self->rowcount = 0L;

    func_args = PyTuple_New(1);
    if (!func_args) {
        goto error;
    }
    Py_INCREF(operation);
    if (PyTuple_SetItem(func_args, 0, operation) != 0) {
        goto error;
    }

    if (self->statement) {
        (void)pysqlite_statement_reset(self->statement);
        Py_DECREF(self->statement);
    }

    self->statement = (pysqlite_Statement*)pysqlite_cache_get(self->connection->statement_cache, func_args);

    if (!self->statement) {
        goto error;
    }

    if (self->statement->in_use) {
        Py_DECREF(self->statement);
        self->statement = PyObject_New(pysqlite_Statement, &pysqlite_StatementType);
        if (!self->statement) {
            goto error;
        }
        rc = pysqlite_statement_create(self->statement, self->connection, operation);
        if (rc != SQLITE_OK) {
            Py_CLEAR(self->statement);
            goto error;
        }
    }

    pysqlite_statement_reset(self->statement);
    pysqlite_statement_mark_dirty(self->statement);

    /* For backwards compatibility, do not start a transaction if a DDL statement is encountered. If anybody
     * wants transactional DDL, they can issue a BEGIN statement manually. */
    if (self->connection->begin_statement && !sqlite3_stmt_readonly(self->statement->st) && !self->statement->is_ddl) {
        if (sqlite3_get_autocommit(self->connection->db)) {
            result = _pysqlite_connection_begin(self->connection);
            if (!result) {
                goto error;
            }
            Py_DECREF(result);
        }
    }

    while (1) {
        parameters = PyIter_Next(parameters_iter);
        if (!parameters) {
            break;
        }

        pysqlite_statement_mark_dirty(self->statement);

        pysqlite_statement_bind_parameters(self->statement, parameters, allow_8bit_chars);
        if (PyErr_Occurred()) {
            goto error;
        }

        rc = pysqlite_step(self->statement->st, self->connection);
        if (rc != SQLITE_DONE && rc != SQLITE_ROW) {
            if (PyErr_Occurred()) {
                /* there was an error that occurred in a user-defined callback */
                if (_enable_callback_tracebacks) {
                    PyErr_Print();
                } else {
                    PyErr_Clear();
                }
            }
            (void)pysqlite_statement_reset(self->statement);
            _pysqlite_seterror(self->connection->db, NULL);
            goto error;
        }

        if (pysqlite_build_row_cast_map(self) != 0) {
            PyErr_SetString(pysqlite_OperationalError, "Error while building row_cast_map");
            goto error;
        }

        if (rc == SQLITE_ROW || rc == SQLITE_DONE) {
            numcols = sqlite3_column_count(self->statement->st);

            if (self->description == Py_None && numcols > 0) {
                Py_DECREF(self->description);
                self->description = PyTuple_New(numcols);
                if (!self->description) {
                    goto error;
                }
                for (i = 0; i < numcols; i++) {
                    descriptor = PyTuple_New(7);
                    if (!descriptor) {
                        goto error;
                    }
                    PyTuple_SetItem(descriptor, 0, _pysqlite_build_column_name(sqlite3_column_name(self->statement->st, i)));
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 1, Py_None);
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 2, Py_None);
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 3, Py_None);
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 4, Py_None);
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 5, Py_None);
                    Py_INCREF(Py_None); PyTuple_SetItem(descriptor, 6, Py_None);
                    PyTuple_SetItem(self->description, i, descriptor);
                }
            }
        }

        if (!sqlite3_stmt_readonly(self->statement->st)) {
            self->rowcount += (long)sqlite3_changes(self->connection->db);
        } else {
            self->rowcount= -1;
        }

        if (!multiple) {
            sqlite_int64 lastrowid;
            Py_DECREF(self->lastrowid);
            Py_BEGIN_ALLOW_THREADS
            lastrowid = sqlite3_last_insert_rowid(self->connection->db);
            Py_END_ALLOW_THREADS
            self->lastrowid = _pysqlite_long_from_int64(lastrowid);
        }

        if (rc == SQLITE_ROW) {
            if (multiple) {
                PyErr_SetString(pysqlite_ProgrammingError, "executemany() can only execute DML statements.");
                goto error;
            }

            self->next_row = _pysqlite_fetch_one_row(self);
        } else if (rc == SQLITE_DONE && !multiple) {
            pysqlite_statement_reset(self->statement);
            Py_CLEAR(self->statement);
        }

        if (multiple) {
            rc = pysqlite_statement_reset(self->statement);
        }
        Py_XDECREF(parameters);
    }

error:
    Py_XDECREF(func_args);
    Py_XDECREF(parameters);
    Py_XDECREF(parameters_iter);
    Py_XDECREF(parameters_list);

    self->locked = 0;

    if (PyErr_Occurred()) {
        self->rowcount = -1L;
        return NULL;
    } else {
        Py_INCREF(self);
        return (PyObject*)self;
    }
}

PyObject* pysqlite_cursor_execute(pysqlite_Cursor* self, PyObject* args)
{
    return _pysqlite_query_execute(self, 0, args);
}

PyObject* pysqlite_cursor_executemany(pysqlite_Cursor* self, PyObject* args)
{
    return _pysqlite_query_execute(self, 1, args);
}

PyObject* pysqlite_cursor_executescript(pysqlite_Cursor* self, PyObject* args)
{
    PyObject* script_obj;
    PyObject* script_str = NULL;
    const char* script_cstr;
    sqlite3_stmt* statement;
    int rc;
    PyObject* result;

    if (!PyArg_ParseTuple(args, "O", &script_obj)) {
        return NULL;
    }

    if (!check_cursor(self)) {
        return NULL;
    }

    self->reset = 0;

    if (PyString_Check(script_obj)) {
        script_cstr = PyString_AsString(script_obj);
    } else if (PyUnicode_Check(script_obj)) {
        script_str = PyUnicode_AsUTF8String(script_obj);
        if (!script_str) {
            return NULL;
        }

        script_cstr = PyString_AsString(script_str);
    } else {
        PyErr_SetString(PyExc_ValueError, "script argument must be unicode or string.");
        return NULL;
    }

    /* commit first */
    result = pysqlite_connection_commit(self->connection, NULL);
    if (!result) {
        goto error;
    }
    Py_DECREF(result);

    while (1) {
        Py_BEGIN_ALLOW_THREADS
        rc = sqlite3_prepare_v2(self->connection->db,
                             script_cstr,
                             -1,
                             &statement,
                             &script_cstr);
        Py_END_ALLOW_THREADS
        if (rc != SQLITE_OK) {
            _pysqlite_seterror(self->connection->db, NULL);
            goto error;
        }

        /* execute statement, and ignore results of SELECT statements */
        rc = SQLITE_ROW;
        while (rc == SQLITE_ROW) {
            rc = pysqlite_step(statement, self->connection);
            /* TODO: we probably need more error handling here */
        }

        if (rc != SQLITE_DONE) {
            (void)sqlite3_finalize(statement);
            _pysqlite_seterror(self->connection->db, NULL);
            goto error;
        }

        rc = sqlite3_finalize(statement);
        if (rc != SQLITE_OK) {
            _pysqlite_seterror(self->connection->db, NULL);
            goto error;
        }

        if (*script_cstr == (char)0) {
            break;
        }
    }

error:
    Py_XDECREF(script_str);

    if (PyErr_Occurred()) {
        return NULL;
    } else {
        Py_INCREF(self);
        return (PyObject*)self;
    }
}

PyObject* pysqlite_cursor_getiter(pysqlite_Cursor *self)
{
    Py_INCREF(self);
    return (PyObject*)self;
}

PyObject* pysqlite_cursor_iternext(pysqlite_Cursor *self)
{
    PyObject* next_row_tuple;
    PyObject* next_row;
    int rc;

    if (!check_cursor(self)) {
        return NULL;
    }

    if (self->reset) {
        PyErr_SetString(pysqlite_InterfaceError, errmsg_fetch_across_rollback);
        return NULL;
    }

    if (!self->next_row) {
         if (self->statement) {
            (void)pysqlite_statement_reset(self->statement);
            Py_CLEAR(self->statement);
        }
        return NULL;
    }

    next_row_tuple = self->next_row;
    self->next_row = NULL;

    if (self->connection->row_factory != Py_None) {
        next_row = PyObject_CallFunction(self->connection->row_factory, "OO", self, next_row_tuple);
        Py_DECREF(next_row_tuple);
    } else {
        next_row = next_row_tuple;
    }

    if (self->statement) {
        rc = pysqlite_step(self->statement->st, self->connection);
        if (rc != SQLITE_DONE && rc != SQLITE_ROW) {
            (void)pysqlite_statement_reset(self->statement);
            Py_DECREF(next_row);
            _pysqlite_seterror(self->connection->db, NULL);
            return NULL;
        }

        if (rc == SQLITE_ROW) {
            self->next_row = _pysqlite_fetch_one_row(self);
        }
    }

    return next_row;
}

PyObject* pysqlite_cursor_fetchone(pysqlite_Cursor* self, PyObject* args)
{
    PyObject* row;

    row = pysqlite_cursor_iternext(self);
    if (!row && !PyErr_Occurred()) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return row;
}

PyObject* pysqlite_cursor_fetchmany(pysqlite_Cursor* self, PyObject* args, PyObject* kwargs)
{
    static char *kwlist[] = {"size", NULL, NULL};

    PyObject* row;
    PyObject* list;
    int maxrows = self->arraysize;
    int counter = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|i:fetchmany", kwlist, &maxrows)) {
        return NULL;
    }

    list = PyList_New(0);
    if (!list) {
        return NULL;
    }

    /* just make sure we enter the loop */
    row = Py_None;

    while (row) {
        row = pysqlite_cursor_iternext(self);
        if (row) {
            PyList_Append(list, row);
            Py_DECREF(row);
        } else {
            break;
        }

        if (++counter == maxrows) {
            break;
        }
    }

    if (PyErr_Occurred()) {
        Py_DECREF(list);
        return NULL;
    } else {
        return list;
    }
}

PyObject* pysqlite_cursor_fetchall(pysqlite_Cursor* self, PyObject* args)
{
    PyObject* row;
    PyObject* list;

    list = PyList_New(0);
    if (!list) {
        return NULL;
    }

    /* just make sure we enter the loop */
    row = (PyObject*)Py_None;

    while (row) {
        row = pysqlite_cursor_iternext(self);
        if (row) {
            PyList_Append(list, row);
            Py_DECREF(row);
        }
    }

    if (PyErr_Occurred()) {
        Py_DECREF(list);
        return NULL;
    } else {
        return list;
    }
}

PyObject* pysqlite_noop(pysqlite_Connection* self, PyObject* args)
{
    /* don't care, return None */
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject* pysqlite_cursor_close(pysqlite_Cursor* self, PyObject* args)
{
    if (!pysqlite_check_thread(self->connection) || !pysqlite_check_connection(self->connection)) {
        return NULL;
    }

    if (self->statement) {
        (void)pysqlite_statement_reset(self->statement);
        Py_CLEAR(self->statement);
    }

    self->closed = 1;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef cursor_methods[] = {
    {"execute", (PyCFunction)pysqlite_cursor_execute, METH_VARARGS,
        PyDoc_STR("Executes a SQL statement.")},
    {"executemany", (PyCFunction)pysqlite_cursor_executemany, METH_VARARGS,
        PyDoc_STR("Repeatedly executes a SQL statement.")},
    {"executescript", (PyCFunction)pysqlite_cursor_executescript, METH_VARARGS,
        PyDoc_STR("Executes a multiple SQL statements at once. Non-standard.")},
    {"fetchone", (PyCFunction)pysqlite_cursor_fetchone, METH_NOARGS,
        PyDoc_STR("Fetches one row from the resultset.")},
    {"fetchmany", (PyCFunction)pysqlite_cursor_fetchmany, METH_VARARGS|METH_KEYWORDS,
        PyDoc_STR("Fetches several rows from the resultset.")},
    {"fetchall", (PyCFunction)pysqlite_cursor_fetchall, METH_NOARGS,
        PyDoc_STR("Fetches all rows from the resultset.")},
    {"close", (PyCFunction)pysqlite_cursor_close, METH_NOARGS,
        PyDoc_STR("Closes the cursor.")},
    {"setinputsizes", (PyCFunction)pysqlite_noop, METH_VARARGS,
        PyDoc_STR("Required by DB-API. Does nothing in pysqlite.")},
    {"setoutputsize", (PyCFunction)pysqlite_noop, METH_VARARGS,
        PyDoc_STR("Required by DB-API. Does nothing in pysqlite.")},
    {NULL, NULL}
};

static struct PyMemberDef cursor_members[] =
{
    {"connection", T_OBJECT, offsetof(pysqlite_Cursor, connection), RO},
    {"description", T_OBJECT, offsetof(pysqlite_Cursor, description), RO},
    {"arraysize", T_INT, offsetof(pysqlite_Cursor, arraysize), 0},
    {"lastrowid", T_OBJECT, offsetof(pysqlite_Cursor, lastrowid), RO},
    {"rowcount", T_LONG, offsetof(pysqlite_Cursor, rowcount), RO},
    {NULL}
};

static char cursor_doc[] =
PyDoc_STR("SQLite database cursor class.");

PyTypeObject pysqlite_CursorType = {
        PyVarObject_HEAD_INIT(NULL, 0)
        MODULE_NAME ".Cursor",                          /* tp_name */
        sizeof(pysqlite_Cursor),                        /* tp_basicsize */
        0,                                              /* tp_itemsize */
        (destructor)pysqlite_cursor_dealloc,            /* tp_dealloc */
        0,                                              /* tp_print */
        0,                                              /* tp_getattr */
        0,                                              /* tp_setattr */
        0,                                              /* tp_compare */
        0,                                              /* tp_repr */
        0,                                              /* tp_as_number */
        0,                                              /* tp_as_sequence */
        0,                                              /* tp_as_mapping */
        0,                                              /* tp_hash */
        0,                                              /* tp_call */
        0,                                              /* tp_str */
        0,                                              /* tp_getattro */
        0,                                              /* tp_setattro */
        0,                                              /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_ITER|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_HAVE_WEAKREFS, /* tp_flags */
        cursor_doc,                                     /* tp_doc */
        0,                                              /* tp_traverse */
        0,                                              /* tp_clear */
        0,                                              /* tp_richcompare */
        offsetof(pysqlite_Cursor, in_weakreflist),      /* tp_weaklistoffset */
        (getiterfunc)pysqlite_cursor_getiter,           /* tp_iter */
        (iternextfunc)pysqlite_cursor_iternext,         /* tp_iternext */
        cursor_methods,                                 /* tp_methods */
        cursor_members,                                 /* tp_members */
        0,                                              /* tp_getset */
        0,                                              /* tp_base */
        0,                                              /* tp_dict */
        0,                                              /* tp_descr_get */
        0,                                              /* tp_descr_set */
        0,                                              /* tp_dictoffset */
        (initproc)pysqlite_cursor_init,                 /* tp_init */
        0,                                              /* tp_alloc */
        0,                                              /* tp_new */
        0                                               /* tp_free */
};

extern int pysqlite_cursor_setup_types(void)
{
    pysqlite_CursorType.tp_new = PyType_GenericNew;
    return PyType_Ready(&pysqlite_CursorType);
}
