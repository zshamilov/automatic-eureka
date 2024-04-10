from sqlalchemy import text

from sdk.user import User


def select_versions_with_same_diagram_id(user: User, diagram_id: str) -> list[dict]:
    """Just for example, also can be used with models"""

    columns = user.with_db.get_column_names('diagram', 'decision')
    query = text(
        f"select {','.join(columns)} from decision.diagram where diagram.diagram_id='{diagram_id}'"
    )

    with user.with_db.engine.connect() as connection:
        results = connection.execute(query).all()

    return [
        dict(zip(columns, row))
        for row in results
    ]
