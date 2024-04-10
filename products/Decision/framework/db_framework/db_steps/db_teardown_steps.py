import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError


# alter table decision.asn_data_provider_to_diagram
# drop constraint asn_data_provider_to_diagram_diagram_version_fk;
#
# DELETE FROM decision.asn_data_provider_to_diagram WHERE from_key in ($ids)
#
# alter table decision.asn_data_provider_to_diagram
# add constraint asn_data_provider_to_diagram_diagram_version_fk
# foreign key (to_key) references decision.diagram (version_id);

def delete_constraint(user):
    qry = sa.text('alter table decision.asn_data_provider_to_diagram '
                  'drop constraint asn_data_provider_to_diagram_diagram_version_fk;')
    print(qry)
    with user.with_db.engine.connect() as connection:
        try:
            connection.execute(qry)
            connection.commit()
        except:
            print("could not drop constraint")
    return


def return_constraint(user):
    qry = sa.text('alter table decision.asn_data_provider_to_diagram add constraint '
                  'asn_data_provider_to_diagram_diagram_version_fk foreign key (to_key) '
                  'references decision.diagram (version_id);')
    print(qry)
    with user.with_db.engine.connect() as connection:
        try:
            connection.execute(qry)
            connection.commit()
        except ProgrammingError:
            print("already_exists")

    return


def delete_from_table(user, object_ids: list):
    object = "'" + "', '".join(object_ids) + "'"
    qry = sa.text(f'DELETE FROM decision.asn_data_provider_to_diagram WHERE from_key in ({object})')
    print(qry)
    with user.with_db.engine.connect() as connection:
        try:
            connection.execute(qry)
            connection.commit()
        except ProgrammingError:
            return_constraint(user)
    return
