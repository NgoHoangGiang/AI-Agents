from typing import List

from pydantic import BaseModel, Field


class ExplainSqlRequest(BaseModel):
    sql: str = Field(..., min_length=1, description="SQL query to explain")


class SqlTableInfo(BaseModel):
    name: str


class SqlJoinInfo(BaseModel):
    join_type: str
    table: str
    condition: str


class ExplainSqlResponse(BaseModel):
    sql: str
    summary: str
    tables: List[SqlTableInfo]
    joins: List[SqlJoinInfo]
    filters: List[str]
    group_by: List[str]
    aggregations: List[str]
    order_by: List[str]
    warnings: List[str]