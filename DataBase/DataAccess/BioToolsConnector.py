
from sqlite3 import Error

import Utility
from settings import db_connection
db = db_connection.connection


def create_biotools_info_table():
    print("Initializing biotools_tools_info...", end=" ")
    try:
        db.execute('''create table biotools_tools_info
                                    (
                                        Biotools_id    TEXT not null
                                            constraint biotools_tools_pk
                                                primary key,
                                        Biotools_CURIE TEXT,
                                        Version        TEXT,
                                        Name           TEXT not null,
                                        Description    TEXT,
                                        Homepage       TEXT,
                                        Documentation  TEXT,
                                        Published      TEXT,
                                        LastUpdate     TEXT
                                    );

        ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_operations_table():
    print("Intializing biotools_tools_operations...", end=" ")
    try:
        db.execute('''create table biotools_tools_operations
                                    (
                                        Biotools_id TEXT    not null
                                            constraint biotools_tools_operations_biotools_tools_info_Biotools_id_fk
                                                references biotools_tools_info,
                                        EDAM_id     integer not null
                                            constraint biotools_tools_operations_EDAM_EDAM_id_fk
                                                references EDAM,
                                        constraint biotools_tools_operations_pk
                                            primary key (Biotools_id, EDAM_id)
                                    );
                                    ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_topics_table():
    print("Intializing biotools_tools_topics...", end=" ")
    try:
        db.execute('''create table biotools_tools_topics
                                    (
                                        Biotools_id TEXT not null
                                            constraint biotools_tools_topics_biotools_tools_info_Biotools_id_fk
                                                references biotools_tools_info,
                                        EDAM_id     TEXT not null
                                            constraint biotools_tools_topics_EDAM_EDAM_id_fk
                                                references EDAM,
                                        constraint biotools_tools_topics_pk
                                            primary key (Biotools_id, EDAM_id)
                                    );
                                    ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_tools_collection():
    print("Intializing biotools_tools_collection...", end=" ")
    try:
        db.execute('''create table biotools_tools_topics
                                            (
                                                Biotools_id TEXT not null
                                                    constraint biotools_tools_topics_biotools_tools_info_Biotools_id_fk
                                                        references biotools_tools_info,
                                                EDAM_id     TEXT not null
                                                    constraint biotools_tools_topics_EDAM_EDAM_id_fk
                                                        references EDAM,
                                                constraint biotools_tools_topics_pk
                                                    primary key (Biotools_id, EDAM_id)
                                            );
                                            ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_tools_type():
    print("Intializing biotools_tools_type...", end=" ")
    try:
        db.execute('''create table biotools_tools_type
                                            (
                                                Biotools_id TEXT not null
                                                    constraint biotools_tools_topics_biotools_tools_info_Biotools_id_fk
                                                        references biotools_tools_info,
                                                Tool_type     TEXT not null,
                                                constraint biotools_tools_topics_pk
                                                    primary key (Biotools_id, Tool_type)
                                            );
                                            ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_tools_inputs():
    print("Initializing biotools_tools_inputs...", end=" ")
    try:
        db.execute('''create table biotools_tools_inputs
            (
                Biotools_id TEXT not null,
                EDAM_id_data     TEXT,
                EDAM_id_format   TEXT,
                constraint biotools_tools_inputs_pk
                    primary key (Biotools_id, EDAM_id_data, EDAM_id_format),
                constraint biotools_tools_inputs_Biotools_id_fk
                    foreign key (Biotools_id) references biotools_tools_info (Biotools_id),
                constraint biotools_tools_inputs_EDAM_id_fk
                    foreign key (EDAM_id_data, EDAM_id_format) references EDAM (EDAM_id, EDAM_id)
            );

            ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_tools_outputs():
    print("Initializing biotools_tools_outputs...", end=" ")
    try:
        db.execute('''create table biotools_tools_outputs
            (
                Biotools_id TEXT not null,
                EDAM_id_data     TEXT,
                EDAM_id_format   TEXT,
                constraint biotools_tools_outputs_pk
                    primary key (Biotools_id, EDAM_id_data, EDAM_id_format),
                constraint biotools_tools_outputs_Biotools_id_fk
                    foreign key (Biotools_id) references biotools_tools_info (Biotools_id),
                constraint biotools_tools_outputs_EDAM_id_fk
                    foreign key (EDAM_id_data, EDAM_id_format) references EDAM (EDAM_id, EDAM_id)
            );
            ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def create_biotools_tables():
    create_biotools_info_table()
    create_biotools_operations_table()
    create_biotools_topics_table()
    create_biotools_tools_type()
    create_biotools_tools_inputs()
    create_biotools_tools_outputs()


def insert_biotools(items):
    for item in items:
        biotools_id = item['biotoolsID']
        try:
            version = item['version'][0]
        except Exception:
            version = None
        biotools_curie = item['biotoolsCURIE']
        name = item['name']
        description = Utility.DB.escape_input(item['description'])
        homepage = item['homepage']
        try:
            docs = item['documentation'][0]['url']
        except Exception:
            docs = None
        published = item['additionDate']
        updated = item['lastUpdate']
        try:
            db.execute(f'''insert into biotools_tools_info (Biotools_id, Version, Biotools_CURIE, Name, Description, Homepage, Documentation,
                                                    Published, LastUpdate)
                                                   values ("{biotools_id}", "{version}", "{biotools_curie}", "{name}", "{description}", "{homepage}", "{docs}", "{published}", "{updated}")
                                                   on conflict do nothing;
                           ''')
        except Error as e:
            print(f"Entry '{biotools_id}' caused error '{str(e)}'")

        for i in range(0, len(item['function'])):
            for op in item['function'][i]['operation']:
                edam_id = op['uri'].split("/")[-1]
                try:
                    db.execute(f'''insert into biotools_tools_operations (Biotools_id, EDAM_id)
                                                   values("{biotools_id}", "{edam_id}") on conflict do nothing
                       ''')
                except Error as e:
                    print(f"biotools_tools_operations: Inserting '{biotools_id}', '{edam_id}' caused error '{str(e)}'")
            for input_item in item['function'][i]['input']:
                data_id = input_item['data']['uri'].split("/")[-1]
                for format_item in input_item['format']:
                    format_id = format_item['uri'].split("/")[-1]
                    db.execute(f'''insert into biotools_tools_inputs (Biotools_id, EDAM_id_data, EDAM_id_format)
                                                values ("{biotools_id}", "{data_id}", "{format_id}") on conflict do nothing''')
            for output_item in item['function'][i]['output']:
                data_id = output_item['data']['uri'].split("/")[-1]
                for format_item in output_item['format']:
                    format_id = format_item['uri'].split("/")[-1]
                    db.execute(f'''insert into biotools_tools_outputs (Biotools_id, EDAM_id_data, EDAM_id_format)
                                                values ("{biotools_id}", "{data_id}", "{format_id}") on conflict do nothing''')
        for topic in item['topic']:
            edam_id = topic['uri'].split("/")[-1]
            try:
                db.execute(f'''insert into biotools_tools_topics (Biotools_id, EDAM_id)
                                               values("{biotools_id}", "{edam_id}") on conflict do nothing
                   ''')
            except Error as e:
                print(f"biotools_tools_topic: Inserting '{biotools_id}', '{edam_id}' caused error '{str(e)}'")

        for tool_type in item['toolType']:
            try:
                db.execute(f'''insert into biotools_tools_type (Biotools_id, Tool_type)
                                            values("{biotools_id}", "{tool_type}") on conflict do nothing
                ''')
            except Error as e:
                print(f"biotools_tools_type: Inserting '{biotools_id}', '{tool_type}' caused error '{str(e)}'")
        if len(item['toolType']) == 0:
            try:
                db.execute(f'''insert into biotools_tools_type (Biotools_id, Tool_type)
                                            values("{biotools_id}", "Unknown") on conflict do nothing
                ''')
            except Error as e:
                print(f"biotools_tools_type: Inserting '{biotools_id}', 'Unknown' caused error '{str(e)}'")
    db.commit()
