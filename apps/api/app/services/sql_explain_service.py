import re
from typing import Dict, List


class SqlExplainService:
    JOIN_PATTERN = re.compile(
        r"\b(?:(LEFT|RIGHT|INNER|FULL|CROSS)\s+)?JOIN\s+([a-zA-Z0-9_.\"]+)(?:\s+(?:AS\s+)?[a-zA-Z0-9_\"]+)?\s+ON\s+(.+?)(?=\b(?:LEFT|RIGHT|INNER|FULL|CROSS)?\s*JOIN\b|\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|\bHAVING\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    FROM_PATTERN = re.compile(
        r"\bFROM\s+([a-zA-Z0-9_.\"]+)(?:\s+(?:AS\s+)?[a-zA-Z0-9_\"]+)?",
        flags=re.IGNORECASE,
    )

    WHERE_PATTERN = re.compile(
        r"\bWHERE\s+(.+?)(?=\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|\bHAVING\b|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    GROUP_BY_PATTERN = re.compile(
        r"\bGROUP\s+BY\s+(.+?)(?=\bORDER\s+BY\b|\bLIMIT\b|\bHAVING\b|$)",
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

    CTE_PATTERN = re.compile(
        r"^\s*WITH\s+([a-zA-Z0-9_]+)\s+AS\s*\(",
        flags=re.IGNORECASE,
    )

    AGG_FUNCTIONS = ["SUM", "COUNT", "AVG", "MIN", "MAX"]

    @staticmethod
    def normalize_sql(sql: str) -> str:
        sql = sql.strip()
        sql = re.sub(r"\s+", " ", sql)
        return sql

    @staticmethod
    def split_csv_like(text: str) -> List[str]:
        return [part.strip() for part in text.split(",") if part.strip()]

    @staticmethod
    def extract_tables(sql: str) -> List[Dict]:
        tables: List[Dict] = []

        from_match = SqlExplainService.FROM_PATTERN.search(sql)
        if from_match:
            tables.append({"name": from_match.group(1).strip()})

        join_matches = SqlExplainService.JOIN_PATTERN.findall(sql)
        for _join_type, table, _condition in join_matches:
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
    def detect_cte(sql: str) -> List[str]:
        matches = SqlExplainService.CTE_PATTERN.findall(sql)
        return [match.strip() for match in matches]

    @staticmethod
    def detect_select_star(sql: str) -> bool:
        match = SqlExplainService.SELECT_PATTERN.search(sql)
        if not match:
            return False

        select_clause = match.group(1).strip()
        return select_clause == "*" or " * " in f" {select_clause} "

    @staticmethod
    def build_summary(
        tables: List[Dict],
        joins: List[Dict],
        filters: List[str],
        group_by: List[str],
        aggregations: List[str],
        order_by: List[str],
        ctes: List[str],
    ) -> str:
        if not tables:
            return "This SQL query could not be clearly analyzed."

        parts: List[str] = []

        if ctes:
            parts.append(f"This query defines CTEs: {', '.join(ctes)}.")

        parts.append(f"This query reads data from {tables[0]['name']}.")

        if len(tables) > 1:
            extra_tables = ", ".join(table["name"] for table in tables[1:])
            parts.append(f"It also uses related tables: {extra_tables}.")

        if joins:
            join_types = ", ".join(join["join_type"] for join in joins)
            parts.append(f"It uses joins ({join_types}).")

        if aggregations:
            parts.append(f"It performs aggregations such as: {', '.join(aggregations)}.")

        if filters:
            parts.append("It applies filtering conditions.")

        if group_by:
            parts.append(f"It groups the result by: {', '.join(group_by)}.")

        if order_by:
            parts.append(f"It sorts the output by: {', '.join(order_by)}.")

        return " ".join(parts)

    @staticmethod
    def build_warnings(
        sql: str,
        tables: List[Dict],
        joins: List[Dict],
        ctes: List[str],
    ) -> List[str]:
        warnings: List[str] = []

        normalized_upper = sql.upper()

        if not normalized_upper.startswith("SELECT") and not normalized_upper.startswith("WITH"):
            warnings.append("This endpoint is designed primarily for SELECT queries.")

        if not tables:
            warnings.append("No source table was confidently detected.")

        if SqlExplainService.detect_select_star(sql):
            warnings.append("Query uses SELECT *, which may be risky in analytics or production queries.")

        if ctes:
            warnings.append("CTE parsing is basic. Review the SQL manually if the logic is complex.")

        if "SUBQUERY" in normalized_upper:
            warnings.append("Subquery parsing is not fully supported yet.")

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
        ctes = SqlExplainService.detect_cte(normalized_sql)

        summary = SqlExplainService.build_summary(
            tables=tables,
            joins=joins,
            filters=filters,
            group_by=group_by,
            aggregations=aggregations,
            order_by=order_by,
            ctes=ctes,
        )

        warnings = SqlExplainService.build_warnings(
            sql=normalized_sql,
            tables=tables,
            joins=joins,
            ctes=ctes,
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