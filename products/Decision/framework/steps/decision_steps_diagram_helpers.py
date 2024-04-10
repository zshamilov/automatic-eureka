import uuid
from typing import List, Any

from products.Decision.framework.model import ScoreMapping, ScoreValue, JsonGenerationDto
from products.Decision.framework.scheme.decision_scheme_diagram_helper import DecisionDiagramHelper
from sdk.user import User


def upload_scorecard_file(user: User, file: str) -> list[ScoreMapping]:
    score_maps: list[ScoreMapping] = []
    response = user.with_api.send(DecisionDiagramHelper.post_scorecard_file(file=file))
    for m in response.body:
        score_map: ScoreMapping = ScoreMapping.construct(**m)
        vals = []
        for val in score_map.scoreValues:
            v = ScoreValue.construct(**val)
            v.rowKey = str(uuid.uuid4())
            v.maxValue = str(int(float(v.maxValue)))
            v.minValue = str(int(float(v.minValue)))
            v.scoreValue = str(int(float(v.scoreValue)))
            vals.append(v)
        score_map.scoreValues = vals
        score_maps.append(score_map)
    return score_maps


def generate_json_from_variables(user: User, body: JsonGenerationDto):
    return user.with_api.send(DecisionDiagramHelper.post_generate_json(body=body))
