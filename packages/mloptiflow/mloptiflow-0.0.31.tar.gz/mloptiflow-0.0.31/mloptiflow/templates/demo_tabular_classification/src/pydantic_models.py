from pydantic import BaseModel, field_validator, ConfigDict
from typing import List


class PredictionInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"features": [1.799e01, 1.038e01, 1.228e02, 1.001e03, 1.184e-01]}
        },
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    features: List[float]

    @field_validator("features")
    @classmethod
    def validate_features_length(cls, v: List[float]) -> List[float]:
        if not v:
            raise ValueError("Features list cannot be empty")
        return v


class PredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predicted_class": 0,
                "class_probabilities": [0.9, 0.1],
                "classes": [0, 1],
            }
        },
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    predicted_class: int
    class_probabilities: List[float]
    classes: List[int]

    @field_validator("class_probabilities")
    @classmethod
    def validate_probabilities(cls, v: List[float]) -> List[float]:
        if not all(0 <= p <= 1 for p in v):
            raise ValueError("All probabilities must be between 0 and 1")
        if abs(sum(v) - 1.0) > 1e-6:
            raise ValueError("Probabilities must sum to 1")
        return v

    @field_validator("classes")
    @classmethod
    def validate_classes_length(cls, v: List[int], values) -> List[int]:
        if "class_probabilities" in values.data:
            if len(v) != len(values.data["class_probabilities"]):
                raise ValueError("Number of classes must match number of probabilities")
        return v
