import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionQueryParams:
    satellite: int | None = None
    ground_station: int | None = None
    status: str | None = None
    date_from: datetime = None
    date_to: datetime = None
    min_tca_elevation: int | None = None

    def to_dict(self) -> dict:
        return {
            'satellite': self.satellite,
            'groundStation': self.ground_station,
            'status': self.status,
            'fromDateTime': self.date_from,
            'toDateTime': self.date_to,
            'minTcaElevation': self.min_tca_elevation
        }
