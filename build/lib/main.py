import json
import random
from typing import Any
import click
from faker import Faker
from sqlalchemy import create_engine
from stopwatch import Stopwatch
from contexts.list_context_impl import ListContextImpl
from structs.raw_value import RawValueAwareEncoder

from structs.schema import Schema
from contexts.document_context_impl import DocumentContextImpl
from writers.csv_line_writer import CsvLineWriter
from writers.db_writer import DbWriter
from writers.sql_file_writer import SqlFileWriter

@click.command()
@click.option('--host', '-h', default='localhost', show_default=True, help='Hostname of machine')
@click.option('--port', '-t', default=5432, show_default=True, help='Port number to connect on')
@click.option('--username', '-u', help='Username to connect with')
@click.option('--password', '-p', hide_input=True, help='Password to connect with')
@click.option('--database', '-d', help='Database name')
@click.option('--write-db', '-w', 'writedb', default=False, is_flag=True)
@click.option('--truncate/--append', default=False, help='Provide --truncate to truncate tables before populating. Tables will be truncated in the reverse order of their appearance in the schema.')
@click.option('--schema', '-s', default='schema.yml', show_default=True, required=True, help='Path to schema file')
@click.option('--output', '-o', type=click.Choice(['json', 'csv', 'sql', 'none'], case_sensitive=False), default='none', help='Output options: json=output JSON to output.json, csv=output to files named after docs, sql=output to output.sql')
def load(host, port, username, password, database, writedb, truncate, schema, output):
    engine = None

    with Stopwatch() as stopwatch:
        if(are_db_params_provided(username, password, database)):
            engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
        
        # Parse the YML file
        parsed_schema = Schema(schema)

        # Prepare our faker data generators
        rand = random.Random(parsed_schema.get_metadata_entry('seed'))
        fake = Faker(['de-DE', 'en-IE', 'es-MX', 'en-US', 'en-GB', 'ga-IE', 'es-ES', 'fil-PH', 'fr-FR', 'it-IT', 'pt-PT', 'nl-BE', 'nl-NL'])
        fake.seed_instance(parsed_schema.get_metadata_entry('seed'))

        # Prepare a home for the results
        resolution_context: dict[str, list[dict[str, Any]]] = dict()

        # Parse the documents
        cache: dict[str, Any] = dict()
        for doc in parsed_schema.list_documents():
            # Skip metadata
            if(doc[:1] == '_'):
                continue;
            
            # Load normal documents
            if(isinstance(parsed_schema.get_document(doc), dict)):
                doc_ctx = DocumentContextImpl(cache, engine, doc, parsed_schema.get_document(doc), resolution_context, fake, rand)
                resolution_context[doc] = doc_ctx.resolve()

            # Load lists of entries
            elif(isinstance(parsed_schema.get_document(doc), list)):
                resolution_context[doc] = ListContextImpl(cache, engine, doc, parsed_schema.get_document(doc), resolution_context, fake, rand).resolve()
            
            # All other types fail
            else:
                raise ValueError(f'Encountered unexpected type for {doc}: {parsed_schema.get_document_type(doc)}')

        # Write JSON file
        if(output == 'json'):
            with open(f'output.json', mode='wt', newline='') as jsonfile:
                jsonfile.write(json.dumps(resolution_context, cls=RawValueAwareEncoder))

        # Write CSV file
        elif(output == 'csv'):
            for doc, entries in resolution_context.items():
                if(len(entries) > 0):
                    with open(f'{doc}.csv', mode='wt', newline='') as csvfile:
                        CsvLineWriter(entries).write(csvfile)

        # Write SQL file
        elif(output == 'sql'):
            with open(f'output.sql', mode='wt', newline='') as sqlfile:
                SqlFileWriter(parsed_schema.get_metadata(), truncate, resolution_context).write(sqlfile)
        
        # Output nothing
        else:
            click.echo("INFO: No output specified")

        # Write to database?
        if(writedb):
            if(are_db_params_provided(username, password, database)):
                DbWriter(parsed_schema, resolution_context, truncate).write_db(engine)
            else:
                click.echo("WARN: ignoring --write-db because not all of --username, --password, and --database were provided")
        else:
            if(truncate):
                click.echo("INFO: not truncating database because --write-db omitted")
            if(are_db_params_provided(username, password, database)):
                click.echo("INFO: DB connection params provided but --write-db omitted")

    click.echo(f"\n\nLoad Completed in {stopwatch.elapsed}s")

def are_db_params_provided(username, password, database):
    return (
        (username != None and len(username) > 0) and 
        (password != None and len(password) > 0) and 
        (database != None and len(database) > 0)
    )

if __name__ == '__main__':
    load()