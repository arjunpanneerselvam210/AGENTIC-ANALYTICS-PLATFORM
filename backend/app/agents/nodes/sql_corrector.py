"""
Node: SQL Corrector & Self-Correction
Re-prompts Ollama Qwen 2.5-Coder to fix validation errors or database execution exceptions.
Increments retry_count and enforces maximum retry limits.
"""

import logging
from app.agents.state import AnalyticsState
from app.agents.prompts import SQL_CORRECTION_SYSTEM_PROMPT
from app.agents.nodes.sql_generator import sanitize_sql
from app.core.llm import ollama_client
from app.core.config import settings

logger = logging.getLogger("agents.sql_corrector")

def correct_sql_node(state: AnalyticsState) -> AnalyticsState:
    """
    Self-corrects failed SQL based on the error message and schema context.
    Increments retry_count.
    """
    retry_count = state.get("retry_count", 0) + 1
    max_retries = state.get("max_retries", 2)
    last_error = state.get("sql_error") or state.get("last_error") or "Unknown SQL error"
    failed_sql = state.get("generated_sql", "")
    question = state.get("original_question", "")
    target_db = state.get("target_database", "company_analytics")
    dialect = "PostgreSQL 16" if "auth" in target_db else "MySQL 8.0"
    schema_text = state.get("schema_context", {}).get("formatted_text", "")

    logger.info(f"Self-correcting SQL for {target_db} ({dialect}) (Attempt {retry_count}/{max_retries}) | Error: {last_error}")

    prompt = (
        f"Original User Question: {question}\n\n"
        f"Target Database: {target_db} ({dialect})\n"
        f"Failed SQL Query:\n{failed_sql}\n\n"
        f"Error Encountered:\n{last_error}\n\n"
        f"Discovered Schema Context:\n{schema_text}\n\n"
        f"Generate the corrected, single read-only {dialect} SELECT statement strictly using discovered schema. Output only raw SQL:"
    )

    messages = [
        {"role": "system", "content": SQL_CORRECTION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    corrected_sql = failed_sql
    try:
        reply = ollama_client.generate_chat_sync(
            messages=messages,
            model=settings.OLLAMA_SQL_MODEL,
            temperature=0.0,
            timeout=20.0
        )
        cleaned = sanitize_sql(reply)
        if cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH"):
            corrected_sql = cleaned
    except Exception as e:
        logger.warning(f"Ollama SQL self-correction failed: {e}")

    # Deterministic safeguard: If LLM repeats non-existent column error (e.g. e.salary), use canonical template
    if "unknown column 'e.salary'" in str(last_error).lower() or "unknown column 'employees.salary'" in str(last_error).lower():
        from app.agents.nodes.sql_generator import canonical_sql_fallback
        fallback = canonical_sql_fallback(question, "HR")
        if fallback:
            logger.info("Applying canonical HR salary SQL fallback after column misidentification.")
            corrected_sql = fallback

    return {
        "retry_count": retry_count,
        "generated_sql": corrected_sql,
        "is_sql_valid": False,
        "sql_error": None
    }
