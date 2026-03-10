"""
Roadmap generation service.
Groups document chunks into daily study sessions based on hours_per_day,
then uses the LLM to generate meaningful titles and descriptions for each day.
"""

import json
import logging

from sqlmodel import Session, select

from app.database import engine
from app.models import Document, DocumentChunk
from app.models.learning_path import LearningPath
from app.models.daily_study_plan import DailyStudyPlan
from app.services.llm_service import generate_response

logger = logging.getLogger(__name__)

# Estimated active study time per chunk (reading + absorbing technical content)
MINUTES_PER_CHUNK = 15


def generate_roadmap(learning_path_id: int) -> None:
    """
    Generate (or regenerate) the daily study roadmap for a learning path.
    - Groups all chunks from the path's documents into days based on hours_per_day.
    - Asks the LLM to produce meaningful day titles and descriptions.
    - Overwrites any existing DailyStudyPlan rows for this path.
    Safe to call multiple times (idempotent — deletes old plans first).
    """
    logger.info("Generating roadmap for learning_path_id=%s", learning_path_id)
    try:
        with Session(engine) as db:
            path = db.get(LearningPath, learning_path_id)
            if not path:
                logger.warning("Learning path %s not found", learning_path_id)
                return

            docs = list(
                db.exec(
                    select(Document)
                    .where(Document.learning_path_id == learning_path_id)
                    .order_by(Document.created_at)
                ).all()
            )

            if not docs:
                path.status = "ready"
                path.total_days = 0
                db.add(path)
                db.commit()
                return

            # Collect all chunks in reading order (doc order → chunk_index)
            all_chunks: list[tuple[int, str, str]] = []  # (chunk_id, content, doc_title)
            for doc in docs:
                chunks = list(
                    db.exec(
                        select(DocumentChunk)
                        .where(DocumentChunk.document_id == doc.id)
                        .order_by(DocumentChunk.chunk_index)
                    ).all()
                )
                for chunk in chunks:
                    all_chunks.append((chunk.id, chunk.content, doc.title))

            if not all_chunks:
                path.status = "ready"
                path.total_days = 0
                db.add(path)
                db.commit()
                return

            chunks_per_day = max(1, round(path.hours_per_day * 60 / MINUTES_PER_CHUNK))

            # Group chunks sequentially into days
            days_data: list[dict] = []
            for i in range(0, len(all_chunks), chunks_per_day):
                day_chunks = all_chunks[i : i + chunks_per_day]
                day_num = (i // chunks_per_day) + 1
                previews = [
                    f"[{c[2]}] {c[1][:200]}" for c in day_chunks[:3]
                ]
                days_data.append(
                    {
                        "day_number": day_num,
                        "chunk_ids": [c[0] for c in day_chunks],
                        "previews": previews,
                        "estimated_minutes": len(day_chunks) * MINUTES_PER_CHUNK,
                    }
                )

            # Ask LLM for day titles/descriptions
            day_labels = _generate_day_labels(
                path.title,
                path.description or "",
                path.hours_per_day,
                days_data,
            )

            # Delete existing plans for this path
            existing = list(
                db.exec(
                    select(DailyStudyPlan).where(
                        DailyStudyPlan.learning_path_id == learning_path_id
                    )
                ).all()
            )
            for plan in existing:
                db.delete(plan)
            db.commit()

            # Insert new plans
            label_map = {item.get("day", item.get("day_number", 0)): item for item in day_labels}
            for day_info in days_data:
                label = label_map.get(day_info["day_number"], {})
                plan = DailyStudyPlan(
                    learning_path_id=learning_path_id,
                    day_number=day_info["day_number"],
                    title=label.get("title") or f"Day {day_info['day_number']}",
                    description=label.get("description"),
                    chunk_ids=day_info["chunk_ids"],
                    estimated_minutes=day_info["estimated_minutes"],
                )
                db.add(plan)

            path.total_days = len(days_data)
            path.status = "ready"
            db.add(path)
            db.commit()

        logger.info(
            "Roadmap generated for learning_path_id=%s: %s days", learning_path_id, len(days_data)
        )

    except Exception as e:
        logger.exception(
            "Roadmap generation failed for learning_path_id=%s: %s", learning_path_id, e
        )
        try:
            with Session(engine) as db:
                path = db.get(LearningPath, learning_path_id)
                if path:
                    path.status = "error"
                    db.add(path)
                    db.commit()
        except Exception:
            pass


def _generate_day_labels(
    path_title: str,
    path_description: str,
    hours_per_day: float,
    days_data: list[dict],
) -> list[dict]:
    """Call the LLM to produce a title + description for each day."""
    if not days_data:
        return []

    days_text = ""
    for day in days_data:
        previews = "\n".join(f"  • {p[:200]}" for p in day["previews"])
        days_text += f"\nDay {day['day_number']} (~{day['estimated_minutes']} min):\n{previews}\n"

    prompt = f"""You are building a structured study roadmap for a learner.

Topic: "{path_title}"
Goal: {path_description or "Not specified"}
Daily study time: {hours_per_day} hour(s)

Below is a preview of the content covered each study day. For each day, generate:
- A concise, descriptive title (max 8 words, e.g. "Introduction to Neural Networks")
- A 1-2 sentence description of what the learner will study

{days_text}

Return ONLY valid JSON — no markdown fences, no extra commentary:
{{"days": [{{"day": 1, "title": "...", "description": "..."}}, ...]}}"""

    try:
        raw = generate_response(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else parts[0]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        return result.get("days", [])
    except Exception as e:
        logger.warning("LLM day label generation failed: %s", e)
        return [
            {"day": d["day_number"], "title": f"Day {d['day_number']}", "description": "Study session"}
            for d in days_data
        ]
