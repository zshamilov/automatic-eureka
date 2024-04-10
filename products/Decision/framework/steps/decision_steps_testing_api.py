from products.Decision.framework.scheme.decision_scheme_testing_api import DecisionTestingApi
from sdk.user import User


def get_tests_list(user: User, query):
    return user.with_api.send(DecisionTestingApi.get_test_list(query=query))


def create_empty_test(user: User, body):
    return user.with_api.send(DecisionTestingApi.post_test_next(body=body))


def delete_test(user: User, test_id):
    return user.with_api.send(DecisionTestingApi.delete_test(test_id=test_id))


def find_test(user: User, test_id):
    return user.with_api.send(DecisionTestingApi.get_test(test_id=test_id))


def get_testing_results(user: User, test_id):
    return user.with_api.send(DecisionTestingApi.get_test_results(test_id=test_id))


def get_testcase_info(user: User, test_case_id):
    return user.with_api.send(DecisionTestingApi.get_test_case(test_case_id=test_case_id))


def update_test(user: User, test_id, body):
    return user.with_api.send(DecisionTestingApi.put_test(test_id=test_id, body=body))


def send_testing_file(user: User, test_id, file):
    return user.with_api.send(DecisionTestingApi.post_testing_file(test_id=test_id, file=file))


def start_testing(user: User, diagram_version_id, body):
    return user.with_api.send(DecisionTestingApi.post_start_testing(
        diagram_version_id=diagram_version_id, body=body))


def download_test_file_gen(user: User, diagram_version_id, file_path):
    return user.with_api.send(request=DecisionTestingApi.get_testing_file_gen(
        diagram_version_id=diagram_version_id), file_path=file_path)


def download_test_file(user: User, test_id, file_path):
    return user.with_api.send(request=DecisionTestingApi.get_testing_file(
        test_id=test_id), file_path=file_path)


def download_test_report(user: User, test_id, file_path):
    return user.with_api.send(request=DecisionTestingApi.get_testing_report(
        test_id=test_id), file_path=file_path)


def get_debug_info(user: User, test_case_id):
    return user.with_api.send(request=DecisionTestingApi.get_test_debug(
        test_case_id=test_case_id))


def get_test_case_result(user: User, test_case_id):
    return user.with_api.send(request=DecisionTestingApi.get_case_result(
        test_case_id=test_case_id))
