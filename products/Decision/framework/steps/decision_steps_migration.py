from products.Decision.framework.scheme.decision_scheme_migration import DecisionMigration
from sdk.user import User


def generate_export_objects(user: User, body):
    return user.with_api.send(DecisionMigration.post_generate_export_objects(body=body))


def set_export(user: User, body):
    return user.with_api.send(DecisionMigration.post_export(body=body))\



def download_export_file(user: User, file_name, file_path=None):
    return user.with_api.send(request=DecisionMigration.get_download_export_file(
        file_name=file_name), file_path=file_path)


def upload_import_file(user: User, file):
    return user.with_api.send(DecisionMigration.post_upload_import_file(file=file))


def confirm_import(user: User, body):
    return user.with_api.send(DecisionMigration.post_import(body=body))
