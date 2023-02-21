# DataFaker

DataFaker is a tool for generating fake data based on a schema. It can dump the results to CSV, SQL, or JSON files. It can also load the data into any database supported by SQLAlchemy.

# Install

To install, clone the project to your local machine and install it like so:

```bash
python3 -m pip install git+ssh://git@migym-gitlab.svc.ac2sp.army.mil:tools/data-faker.git

or 

python3 -m pip install git+https://migym-gitlab.svc.ac2sp.army.mil/migym/webapp.git

or

python3 setup.py install
```

# Usage

```bash
Usage: datafaker [OPTIONS]

Options:
  -h, --host TEXT                 Hostname of machine  [default: localhost]
  -t, --port INTEGER              Port number to connect on  [default: 5432]
  -u, --username TEXT             Username to connect with
  -p, --password TEXT             Password to connect with
  -d, --database TEXT             Database name
  -w, --write-db
  --truncate / --append           Provide --truncate to truncate tables before
                                  populating. Tables will be truncated in the
                                  reverse order of their appearance in the
                                  schema.
  -s, --schema TEXT               Path to schema file  [default: schema.yml;
                                  required]
  -o, --output [json|csv|sql|none]
                                  Output options: json=output JSON to
                                  output.json, csv=output to files named after
                                  docs, sql=output to output.sql
  --help                          Show this message and exit.
```

Using `-w`, `--write-db` or `--truncate` requires you supply database connection parameters: host, port, username, and password.

## Schema

DataFaker generates data based on a schema you provide in the form of a YAML file. By default, DataFaker looks for `schema.yml` in the directory from which you execute it.

### Top-level Metadata

The following properties can be specified at the top-level of the YAML file:

| Property             | Type         | Description                                                                                                        |
| -------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------ |
| \_seed               | integer      | Seeds random data generators. If provided, DataFaker will produce the same output for all runs (except for dates). |
| \_pre_sql            | list[string] | SQL commands to be executed before database tables are truncated.                                                  |
| \_after_truncate_sql | list[string] | SQL commands to be executed after database tables are truncated but before data is loaded.                         |
| \_post_sql           | list[string] | SQL commands to be executed after all data has been loaded.                                                        |

### Documents

The schema file is composed of documents. Each document represents a data entity with related fields. When loading data to a database, each document maps directly to a database table.

Here is a sample `schema.yml` file with a `_seed` metadata property and 2 documents. DataFaker will create 5 random entries for the `users` document. Then, because of the `_from_doc` metadata property, DataFaker will create 1 `users_roles` entry for each `users` entry.

`_from_doc` essentially performs a JOIN to the `users` document. The `from_field('id')` function uses the `users.id` property from the JOIN to populate the `users_roles.user_id` property.

```yaml
_seed: 919
users:
    _count: 5
    id: sequence()
    first_name: fake.first_name()
    last_name: fake.last_name()
users_roles:
    _from_doc:
        doc: users
    user_id: from_field('id')
    role_name: one_of(['ADMIN', 'TEAM_LEADER', 'STAFF'])
```

Documents can be either _dynamic_ or _static_. The documents above are dynamic because they are functionally generated.

Static documents contain a list of entries instead of a pattern of properties. Therefore, DataFaker will create each entry you provide and no more.

Here is an example of a static document. This will generate exactly 3 entries. Each entry will be created uniquely according to the specified property values. Static documents are useful when you need to guarantee certain values are used for each entry.

```yaml
app_settings:
    - id: sequence()
      name: string('show_welcome')
      value: boolean(True)
    - id: sequence()
      name: string('require_otp')
      value: boolean(True)
    - id: sequence()
      name: string('min_password_length')
      value: integer(12)
```

#### Document-level Metadata

Documents can have the following metadata properties:

| Property        | Type    | Description                                                                                                                                                                                                                                                                                 |
| --------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_count`        | integer | Specifies how many entries will be generated for the document.                                                                                                                                                                                                                              |
| `_from_doc`     | dict    | Metadata that describes how to use a previous document as the source for the current document.                                                                                                                                                                                              |
| `_from_sql`     | dict    | Metadata that describes how to use a SQL query as the source for the current document.                                                                                                                                                                                                      |
| `_many_to_many` | dict    | Metadata that describes how to use the cartesian product of two documents, two SQL queries, or a document and a SQL query as the source for the current document.                                                                                                                           |
| `_empty`        | boolean | A **flag** indicating no entries should be generated for the document. This is only useful if you want any data in the document's corresponding SQL table to be truncated while not inserting any new data. You may set it to either `True` or `False`. The effect is the same, either way. |

### Joins

There are three possible joins:

1. `_from_doc`: join to a previous document
2. `_from_sql`: join to the results of a SQL query
3. `_many_to_many`: join to the results of a cartesian product between two documents, two SQL queries, or a document and a SQL query

#### `_from_doc`

Dynamic documents can be joined to other documents so that the child document creates one entry for each entry created by the parent document.

`_from_doc` may contain the following fields:

| Field      | Type       | Description                                                                                                            |
| ---------- | ---------- | ---------------------------------------------------------------------------------------------------------------------- |
| `doc`      | string     | Name of the previous document to use as the source for the current document.                                           |
| `limit`    | integer    | A maximum number of records that may be generated from the document specified by `_from_doc.doc`                       |
| `filter`   | expression | Python expression that evaluates to a boolean value. If `True`, a record is emitted. If `False`, no record is emitted. |
| `multiply` | integer    | A multiplier _x_ that causes _x_ number of records to be produced for every 1 record in the source document.           |

In this example, three `users_roles` entries are created using the first three `users` entries where `active` is true as the sources. The `users.id` property is used to populate the `users_roles.user_id` property.

```yaml
_seed: 919
users:
    _count: 5
    id: sequence()
    first_name: fake.first_name()
    last_name: fake.last_name()
    active: fake.boolean()
users_roles:
    _from_doc:
        doc: users
        limit: 3
        filter: active == True
    user_id: from_field('id')
    role_name: one_of(['ADMIN', 'TEAM_LEADER', 'STAFF'])
```

#### `_from_sql`

Dynamic documents can also be joined to **pre-existing** SQL data. Because changes are not applied to databases until after the all data has been generated, you cannot join to SQL data being created by DataFaker.

`_from_sql` may contain the following fields:

| Field      | Type       | Description                                                                                                                                                  |
| ---------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `sql`      | string     | A query used to pull one or more columns of data that will be stored as a Python `dict`. Each field will be made accessible via `from_field('column_name')`. |
| `limit`    | integer    | A maximum number of records that may be generated from the result set of the SQL query.                                                                      |
| `filter`   | expression | Python expression that evaluates to a boolean value. If `True`, a record is emitted. If `False`, no record is emitted                                        |
| `multiply` | integer    | A multiplier _x_ that causes _x_ number of records to be produced for every 1 record in the result set of the SQL query.                                     |

The example below joins `course_registrations` to pre-existing `students` records. Three `course_registrations` entries will be created for every row in the `students` table up to a maximum of 50 entries. The `student_id` field will be populated by the `students.id` column.

```yaml
course_registrations:
    _from_sql:
        sql: SELECT id FROM students
        limit: 50
        multiply: 3
    student_id: from_field('id')
    course_id: one_of_sql('SELECT id FROM courses')
    registration_date: (now() - days(random_int(0, 15))).isoformat()
```

#### `_many_to_many`

There are times where you need to use the Cartesian product of two documents, two SQL queries, or a document and a SQL query. A good use case for this feature is populating a join table in a database. `_many_to_many` makes this possible.

`_many_to_many` may contain the following fields:

| Field          | Type       | Description                                                                                                                                                                                                                       |
| -------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `left_doc`     | string     | Name of the document used on the left side of the join.                                                                                                                                                                           |
| `right_doc`    | string     | Name of the document used on the right side of the join.                                                                                                                                                                          |
| `left_sql`     | string     | SQL query whose result set will be used on the left side of the join.                                                                                                                                                             |
| `right_sql`    | string     | SQL query whose result set will be used on the right side of the join.                                                                                                                                                            |
| `left_filter`  | expression | Python expression that evaluates to a boolean value. You may reference the properties/column names from the left side of the join. If `True` and `right_filter` is `True`, a record is emitted. If `False`, no record is emitted. |
| `right_filter` | expression | Python expression that evaluates to a boolean value. You may reference the properties/column names from the right side of the join. If `True` and `left_filter` is `True`, a record is emitted. If `False`, no record is emitted. |
| `limit`        | integer    | A maximum number of records that may be generated from the Cartesian product of this join.                                                                                                                                        |

Properties of a `_many_to_many` join __MUST__ preface `from_field('...')` field names with either `left.` or `right.` to specify which side of the join the field is found in.

The example below joins `classes` to `students` and uses their Cartesian product as the source for `registrations`. Up to 1000 entries will be created. Only `students` that are `enrolled` will be used thanks to the `right_filter` expression.

```yaml
registrations:
    _many_to_many:
        limit: 1000
        left_doc: classes
        right_doc: students
        right_filter: enrolled == True
    user_id: from_field('right.id')
    class_id: from_field('left.id')
    registration_date: one_of([ (fromisoformat(from_field('left.start_date')) - days(1)).isoformat(), None ])
    approved: fake.boolean()
```

### Properties

Non-metadata/non-join properties _must_ be valid Python expressions. They may include any standard Python syntax. The following object references and functions are made available in schemas.

#### `fake`

The [Python Faker](https://github.com/joke2k/faker) library is made available via the `fake` object reference. This object reference is limited to the `en-US` locale.

Here are some examples of using it in a schema:

```yaml
users:
    _count: 5
    first_name: fake.first_name()
    last_name: fake.last_name()
    home_state: fake.state_abbr()
    opt_in_email: fake.boolean()
```

#### Functions

Below is the comprehensive list of functions available along with examples.

| Signature                                        | Description                                                                                                                                                                   | Example                                                                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `sequence(start: int = 0, step: int = 1) -> int` | Produces a sequence of consecutive integers starting at 0 for the entries within a document.                                                                                  | `sequence(10, 10)` will produce 10, 20, 30, ...                                                               |
| `first_name()`                                   | Generates a random first name from one of these locales: 'de-DE', 'en-IE', 'es-MX', 'en-US', 'en-GB', 'ga-IE', 'es-ES', 'fil-PH', 'fr-FR', 'it-IT', 'pt-PT', 'nl-BE', 'nl-NL' | `first_name()`                                                                                                |
| `last_name()`                                    | Generates a random last name from one of these locales: 'de-DE', 'en-IE', 'es-MX', 'en-US', 'en-GB', 'ga-IE', 'es-ES', 'fil-PH', 'fr-FR', 'it-IT', 'pt-PT', 'nl-BE', 'nl-NL'  | `last_name()`                                                                                                 |
| `random_char()`                                  | Produces a random uppercase character from the English language.                                                                                                              | `random_char()`                                                                                               |
| `random_int(min: int = 0, max: int = 10) -> int` | Produces a random integer bounded inclusively by `min` and `max`.                                                                                                             | `random_int(5, 10)` could produce 5, 6, 7, 8, 9, or 10.                                                       |
| `digits(length: int) -> str`                     | Produces a string of randomly generated integers. The string will be left-padded by zeroes.                                                                                   | `digits(5)` could produce `00359`.                                                                            |
| `one_of_doc(key: str) -> Any`                    | Randomly selects a property value from the entries of a previous document. The list of possible values is cached for performance.                                             | `one_of_doc('users.id')` would randomly select a value from the `id` field of the `users` document.           |
| `one_of_sql(query: str) -> Any`                  | Randomly selects a value from the results of the provided SQL query. Results are cached for performance.                                                                      | `one_of_sql('SELECT id FROM users')` would randomly select a value from the `id` column of the `users` table. |
| `one_of(options: list[Any]) -> Any`              | Randomly selects a value from the provided list of values.                                                                                                                    | `one_of(['dogs', 'cats', 'birds', 'rabbits'])`                                                                |
| `sql(query: str) -> Any`                         | **Immediately** executes the SQL for every record emitted. The first column returned will be used. If performance is a concern, avoid using this function.                    | `sql('SELECT nextval('user_id_sequence')')`                                                                   |
| `field(name: str) -> Any`                        | Returns the value of another field in the same document entry.                                                                                                                | `field('address')`                                                                                            |
| `now() -> datetime`                              | Returns the current system time as a `datetime` object.                                                                                                                       | `now()`                                                                                                       |
| `milliseconds(delta: int)`                       | Creates a time delta for doing `datetime` math.                                                                                                                               | `(now() - milliseconds(500)).isoformat()`                                                                     |
| `seconds(delta: int)`                            | Creates a time delta for doing `datetime` math.                                                                                                                               | `(now() - seconds(10)).isoformat()`                                                                           |
| `minutes(delta: int)`                            | Creates a time delta for doing `datetime` math.                                                                                                                               | `(now() - minutes(30)).isoformat()`                                                                           |
| `hours(delta: int)`                              | Creates a time delta for doing `datetime` math.                                                                                                                               | `(now() - hours(12)).isoformat()`                                                                             |
| `days(delta: int)`                               | Creates a time delta for doing `datetime` math.                                                                                                                               | `(now() - days(1)).isoformat()`                                                                               |
| `integer(value: Any)`                            | Casts `value` to the `int` type.                                                                                                                                              | `integer('35')`                                                                                               |
| `floating(value: Any)`                           | Casts `value` to the `float` type.                                                                                                                                            | `integer('3.14')`                                                                                             |
| `boolean(value: Any)`                            | Casts `value` to the `bool` type.                                                                                                                                             | `boolean('')` == `False` <br/> `boolean('some_value')` == `True`                                              |
| `string(value: Any)`                             | Casts `value` to the `str` type.                                                                                                                                              | `string(1.234)`                                                                                               |
| `upper(value: str)`                              | Returns `value` in uppercase.                                                                                                                                                 | `upper('abcd')` == 'ABCD'                                                                                     |
| `lower(value: str)`                              | Returns `value` in lowercase.                                                                                                                                                 | `lower('ABCD')` == 'abcd'                                                                                     |
| `raw(value: str)`                                | Used to pass raw SQL directly to the `INSERT` queries produced when loading a database.                                                                                       | `raw('CURRENT_TIMESTAMP')`                                                                                    |

#### A Note About Literal String Values

The YAML parser used by this tool strips surrounding quotes from all YAML properties. Thus, if you want to set a property to a literal string, you will need to use the `string(value: Any)` function. Otherwise, Python will try to evaluate it as an expression rather than a literal string.
