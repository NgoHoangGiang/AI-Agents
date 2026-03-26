import re
from typing import Dict, List


class SqlExplainService:
    JOIN_PATTERN = re.compile(
        r"\b(?:(LEFT|RIGHT|INNER|FULL|CROSS)\s+)?JOIN\s+([a-zA-Z0-9_.\"]+)(?:\s+[a-zA-Z0-9_\"]+)?\s+ON\s+(.+?)(?=\b(?:LEFT|RIGHT|INNER|FULL|CROSS)?\s*JOIN\b|\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    FROM_PATTERN = re.compile(
        r"\bFROM\s+([a-zA-Z0-9_.\"]+)",
        flags=re.IGNORECASE,
    )

    WHERE_PATTERN = re.compile(
        r"\bWHERE\s+(.+?)(?=\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    GROUP_BY_PATTERN = re.compile(
        r"\bGROUP\s+BY\s+(.+?)(?=\bORDER\s+BY\b|\bLIMIT\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    ORDER_BY_PATTERN = re.compile(
        r"\bORDER\s+BY\s+(.+?)(?=\bLIMIT\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    SELECT_PATTERN = re.compile(
        r"\bSELECT\s+(.+?)\bFROM\b",
        flags=re.IGNORECASE | re.DOTALL,
    )

    AGG_FUNCTIONS = ["SUM", "COUNT", "AVG", "MIN", "MAX"]

    @staticmethod
    def normalize_sql(sql: str) -> str:
        sql = sql.strip()
        sql = re.sub(r"\s+", " ", sql)
        return sql

    @staticmethod
    def extract_tables(sql: str) -> List[Dict]:
        tables: List[Dict] = []
        from_match = SqlExplainService.FROM_PATTERN.search(sql)
        if from_match:
            tables.append({"name": from_match.group(1).strip()})

        join_matches = SqlExplainService.JOIN_PATTERN.findall(sql)
        for join_type, table, _condition in join_matches:
            table_name = table.strip()
            if not any(t["name"] == table_name for t in tables):
                tables.append({"name": table_name})

        return tables

    @staticmethod
    def extract_joins(sql: str) -> List[Dict]:
        joins: List[Dict] = []

        for join_type, table, condition in SqlExplainService.JOIN_PATTERN.findall(sql):
            joins.append(
                {
                    "join_type": (join_type or "JOIN").upper(),
                    "table": table.strip(),
                    "condition": condition.strip(),
                }
            )

        return joins

    @staticmethod
    def split_csv_like(text: str) -> List[str]:
        parts = [part.strip() for part in text.split(",") if part.strip()]
        return parts

    @staticmethod
    def extract_filters(sql: str) -> List[str]:
        match = SqlExplainService.WHERE_PATTERN.search(sql)
        if not match:
            return []

        where_clause = match.group(1).strip()
        filters = re.split(r"\bAND\b", where_clause, flags=re.IGNORECASE)
        return [f.strip() for f in filters if f.strip()]

    @staticmethod
    def extract_group_by(sql: str) -> List[str]:
        match = SqlExplainService.GROUP_BY_PATTERN.search(sql)
        if not match:
            return []

        return SqlExplainService.split_csv_like(match.group(1).strip())

    @staticmethod
    def extract_order_by(sql: str) -> List[str]:
        match = SqlExplainService.ORDER_BY_PATTERN.search(sql)
        if not match:
            return []

        return SqlExplainService.split_csv_like(match.group(1).strip())

    @staticmethod
    def extract_aggregations(sql: str) -> List[str]:
        match = SqlExplainService.SELECT_PATTERN.search(sql)
        if not match:
            return []

        select_clause = match.group(1)
        aggregations: List[str] = []

        for func in SqlExplainService.AGG_FUNCTIONS:
            pattern = re.compile(rf"\b{func}\s*\(.+?\)", flags=re.IGNORECASE)
            found = pattern.findall(select_clause)
            aggregations.extend([item.strip() for item in found])

        return aggregations

    @staticmethod
    def build_summary(
        tables: List[Dict],
        joins: List[Dict],
        filters: List[str],
        group_by: List[str],
        aggregations: List[str],
        order_by: List[str],
    ) -> str:
        if not tables:
            return "This SQL query could not be clearly analyzed."

        base = f"This query reads data from {tables[0]['name']}."

        if joins:
            joined_tables = ", ".join(join["table"] for join in joins)
            base += f" It joins additional tables: {joined_tables}."

        if aggregations:
            base += " It performs aggregations."

        if filters:
            base += " It applies filtering conditions."

        if group_by:
            base += " It groups the result set."

        if order_by:
            base += " It sorts the output."

        return base

    @staticmethod
    def build_warnings(sql: str, tables: List[Dict], joins: List[Dict]) -> List[str]:
        warnings: List[str] = []

        if not sql.strip().upper().startswith("SELECT"):
            warnings.append("This endpoint is designed primarily for SELECT queries.")

        if not tables:
            warnings.append("No source table was confidently detected.")

        if "SELECT *" in sql.upper():
            warnings.append("Query uses SELECT *, which may be risky in production analytics queries.")

        for join in joins:
            if not join["condition"]:
                warnings.append(f"Join with {join['table']} has no clearly parsed condition.")

        return warnings

    @staticmethod
    def explain(sql: str) -> Dict:
        normalized_sql = SqlExplainService.normalize_sql(sql)

        tables = SqlExplainService.extract_tables(normalized_sql)
        joins = SqlExplainService.extract_joins(normalized_sql)
        filters = SqlExplainService.extract_filters(normalized_sql)
        group_by = SqlExplainService.extract_group_by(normalized_sql)
        aggregations = SqlExplainService.extract_aggregations(normalized_sql)
        order_by = SqlExplainService.extract_order_by(normalized_sql)

        summary = SqlExplainService.build_summary(
            tables=tables,
            joins=joins,
            filters=filters,
            group_by=group_by,
            aggregations=aggregations,
            order_by=order_by,
        )

        warnings = SqlExplainService.build_warnings(
            sql=normalized_sql,
            tables=tables,
            joins=joins,
        )

        return {
            "sql": sql,
            "summary": summary,
            "tables": tables,
            "joins": joins,
            "filters": filters,
            "group_by": group_by,
            "aggregations": aggregations,
            "order_by": order_by,
            "warnings": warnings,
        }