"""
Server-Side SQL Security Validator for FreshMart MCP Server
Enforces strict read-only execution:
- Only allows SELECT and WITH ... SELECT statements.
- Rejects all data-modifying statements (INSERT, UPDATE, DELETE, REPLACE).
- Rejects all DDL statements (DROP, ALTER, CREATE, TRUNCATE, RENAME).
- Rejects administrative and security operations (GRANT, REVOKE, CALL, FLUSH).
- Rejects multiple statements (SQL injection / batch chaining).
- Rejects file read/write operations (INTO OUTFILE, INTO DUMPFILE, LOAD_FILE).
- Rejects locking clauses (FOR UPDATE, LOCK IN SHARE MODE).
- Blocks access to external databases (e.g., PostgreSQL company_auth, mysql, sys).
"""

import re
from dataclasses import dataclass
from typing import Optional, Set
import sqlparse
from sqlparse.sql import Statement, Token, TokenList
from sqlparse.tokens import Keyword, DML, DDL, Punctuation

@dataclass
class SQLValidationResult:
    is_valid: bool
    error: Optional[str] = None
    sanitized_sql: Optional[str] = None
    statement_type: Optional[str] = None

class SQLValidator:
    """
    Validates SQL queries against strict read-only rules before execution.
    Acts as the primary application-level security boundary for AI agents.
    """

    DISALLOWED_STATEMENT_TYPES = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "TRUNCATE", "RENAME", "REPLACE", "MERGE"
    }

    DISALLOWED_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
        "RENAME", "REPLACE", "MERGE", "GRANT", "REVOKE", "LOCK", "UNLOCK",
        "FLUSH", "RESET", "PURGE", "KILL", "SHUTDOWN", "LOAD", "CALL",
        "EXECUTE", "PREPARE", "DEALLOCATE", "SET", "START", "COMMIT", "ROLLBACK",
        "SAVEPOINT", "HANDLER", "DO", "ALTERUSER", "CREATEUSER", "DROPUSER"
    }

    DISALLOWED_CLAUSES = [
        (re.compile(r"\bINTO\s+OUTFILE\b", re.IGNORECASE), "INTO OUTFILE is forbidden"),
        (re.compile(r"\bINTO\s+DUMPFILE\b", re.IGNORECASE), "INTO DUMPFILE is forbidden"),
        (re.compile(r"\bLOAD_FILE\b", re.IGNORECASE), "LOAD_FILE() function is forbidden"),
        (re.compile(r"\bFOR\s+UPDATE\b", re.IGNORECASE), "Locking clause FOR UPDATE is forbidden"),
        (re.compile(r"\bLOCK\s+IN\s+SHARE\s+MODE\b", re.IGNORECASE), "Locking clause is forbidden"),
        (re.compile(r"\bFOR\s+SHARE\b", re.IGNORECASE), "Locking clause FOR SHARE is forbidden"),
    ]

    DISALLOWED_SCHEMAS = [
        "company_auth",
        "mysql",
        "performance_schema",
        "information_schema.user_privileges",
        "sys",
        "pg_catalog"
    ]

    def __init__(self, max_sql_length: int = 10000):
        self.max_sql_length = max_sql_length

    def validate_sql(self, sql: str) -> SQLValidationResult:
        """
        Validates the incoming SQL string according to security rules.
        Returns SQLValidationResult indicating validity, error details, and cleaned SQL.
        """
        if not sql or not isinstance(sql, str):
            return SQLValidationResult(
                is_valid=False,
                error="SQL query must be a non-empty string."
            )

        sql_stripped = sql.strip()
        if not sql_stripped:
            return SQLValidationResult(
                is_valid=False,
                error="SQL query cannot be empty or blank."
            )

        # 1. Check SQL length limit
        if len(sql_stripped) > self.max_sql_length:
            return SQLValidationResult(
                is_valid=False,
                error=f"SQL length exceeds maximum allowed limit of {self.max_sql_length} characters."
            )

        # 2. Check disallowed clauses (regex scan before full parsing)
        for pattern, error_msg in self.DISALLOWED_CLAUSES:
            if pattern.search(sql_stripped):
                return SQLValidationResult(
                    is_valid=False,
                    error=f"Security violation: {error_msg}."
                )

        # 3. Check for references to unauthorized or external databases
        sql_lower = sql_stripped.lower()
        for schema in self.DISALLOWED_SCHEMAS:
            if f"{schema}." in sql_lower or f"`{schema}`." in sql_lower:
                return SQLValidationResult(
                    is_valid=False,
                    error=f"Security violation: Access to external or administrative database '{schema}' is forbidden."
                )

        # 4. Parse statements using sqlparse
        try:
            parsed = sqlparse.parse(sql_stripped)
        except Exception as e:
            return SQLValidationResult(
                is_valid=False,
                error=f"SQL syntax could not be parsed: {str(e)}"
            )

        # Filter out empty statements (e.g. accidental trailing semicolons or whitespace)
        statements = [s for s in parsed if str(s).strip(";\t\r\n ")]

        if not statements:
            return SQLValidationResult(
                is_valid=False,
                error="No valid SQL statement found."
            )

        # 5. Enforce single-statement policy (anti SQL-injection / batch execution)
        if len(statements) > 1:
            return SQLValidationResult(
                is_valid=False,
                error="Security violation: Multiple SQL statements are not permitted in a single request."
            )

        stmt = statements[0]
        stmt_type = stmt.get_type()

        # 6. Verify statement is purely read-only (SELECT or WITH ... SELECT or EXPLAIN SELECT)
        # Note: sqlparse returns 'SELECT' for SELECT and WITH statements.
        first_token = self._get_first_meaningful_token(stmt)
        if not first_token:
            return SQLValidationResult(
                is_valid=False,
                error="Could not determine statement type."
            )

        first_token_val = first_token.value.upper()
        if first_token_val not in ("SELECT", "WITH", "EXPLAIN"):
            return SQLValidationResult(
                is_valid=False,
                error=f"Forbidden statement type: Only read-only SELECT queries are allowed (found '{first_token_val}')."
            )

        # If EXPLAIN, ensure it only explains a SELECT
        if first_token_val == "EXPLAIN":
            tokens_after = [t.value.upper() for t in stmt.tokens if not t.is_whitespace and t != first_token]
            if not tokens_after or tokens_after[0] not in ("SELECT", "WITH"):
                return SQLValidationResult(
                    is_valid=False,
                    error="EXPLAIN is only permitted for SELECT queries."
                )

        # 7. Deep scan of tokens for any disallowed keywords in any subclause / CTE / subquery
        disallowed_found = self._check_disallowed_tokens(stmt)
        if disallowed_found:
            return SQLValidationResult(
                is_valid=False,
                error=f"Security violation: Forbidden keyword '{disallowed_found}' is not permitted."
            )

        # 8. Clean and format SQL
        # Strip trailing semicolon for database drivers that prefer clean single statements
        cleaned_sql = sql_stripped.rstrip("; \t\r\n")

        return SQLValidationResult(
            is_valid=True,
            sanitized_sql=cleaned_sql,
            statement_type=first_token_val
        )

    def _get_first_meaningful_token(self, stmt: Statement) -> Optional[Token]:
        """Finds the first non-whitespace, non-comment token in the statement."""
        for token in stmt.tokens:
            if not token.is_whitespace and not isinstance(token, sqlparse.sql.Comment):
                return token
        return None

    def _check_disallowed_tokens(self, token_list: TokenList) -> Optional[str]:
        """Recursively checks tokens for any forbidden keywords or operations."""
        for token in token_list.tokens:
            if token.is_group:
                found = self._check_disallowed_tokens(token)
                if found:
                    return found
            else:
                val = token.value.strip().upper()
                # Check exact keyword match
                if val in self.DISALLOWED_KEYWORDS:
                    return val
        return None

# Singleton validator instance
default_validator = SQLValidator()

def validate_sql_security(sql: str) -> tuple[bool, Optional[str]]:
    """
    Convenience function returning (is_valid, error_message).
    """
    res = default_validator.validate_sql(sql)
    return res.is_valid, res.error

