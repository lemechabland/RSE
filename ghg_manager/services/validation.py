"""Validation helpers for incoming data records."""

from typing import Dict, List


class Validator:
    """Validate user input and imported datasets."""

    REQUIRED_ACTIVITY_FIELDS = ["name", "activity_type", "amount", "unit", "emission_factor_key", "scope"]

    def validate_activity(self, record: Dict[str, object]) -> List[str]:
        missing = [field for field in self.REQUIRED_ACTIVITY_FIELDS if field not in record]
        return missing
