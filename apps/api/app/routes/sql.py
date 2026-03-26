from fastapi import APIRouter, HTTPException

from app.schemas.sql import ExplainSqlRequest, ExplainSqlResponse, SqlJoinInfo, SqlTableInfo
from app.services.sql_explain_service import SqlExplainService

router = APIRouter(prefix="/explain-sql", tags=["sql"])


@router.post("", response_model=ExplainSqlResponse)
def explain_sql(request: ExplainSqlRequest) -> ExplainSqlResponse:
    sql = request.sql.strip()

    if not sql:
        raise HTTPException(status_code=400, detail="SQL must not be empty")

    result = SqlExplainService.explain(sql=sql)

    return ExplainSqlResponse(
        sql=result["sql"],
        summary=result["summary"],
        tables=[SqlTableInfo(**item) for item in result["tables"]],
        joins=[SqlJoinInfo(**item) for item in result["joins"]],
        filters=result["filters"],
        group_by=result["group_by"],
        aggregations=result["aggregations"],
        order_by=result["order_by"],
        warnings=result["warnings"],
    )