from pydantic import BaseModel, Field, ConfigDict

class AgentReport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    summary: str = Field(min_length=5, max_length=500)
    recommendation: str = Field(min_length=5, max_length=500)
    limitations: str = Field(min_length=5, max_length=500)

def validate_detection(data: dict) -> None:
    if data['people'] != data['counts']['person']:
        raise ValueError('Person count mismatch')
    if any(v < 0 for v in data['counts'].values()):
        raise ValueError('Negative object count')
    if data['status'] not in {'비어 있음', '소규모', '보통', '혼잡'}:
        raise ValueError('Unknown status')
