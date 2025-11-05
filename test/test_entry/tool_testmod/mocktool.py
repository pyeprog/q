from dataclasses import dataclass
from typing import Literal


@dataclass
class MockEmployee:
    name: str
    age: int
    gender: Literal['Male', 'Female']
    salary: int


def employees(id: str) -> MockEmployee:
    return MockEmployee(name="Jane Doe", age=38, gender="Female", salary=0)
