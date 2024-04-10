from products.Decision.framework.scheme.decision_scheme_integration import DecisionIntegration
from sdk.user import User


def send_message(user: User, call_uri, body):
    return user.with_api.send(DecisionIntegration.post_integration(call_uri=call_uri,
                                                                   body=body))
