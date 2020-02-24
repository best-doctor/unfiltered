from typing_extensions import TypedDict


class Employee(TypedDict):
    id: str  # noqa: VNE003
    first_name: str
    last_name: str
