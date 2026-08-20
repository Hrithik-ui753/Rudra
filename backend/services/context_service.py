import re
import datetime
from typing import Dict, Any, List, Optional, Tuple
from models.schemas import ConversationContext, EntityMemory
from utils.logger import logger


class ConversationContextService:
    """
    Context-Aware Conversation & Entity Memory Management Service.
    Manages turn context, entity memory, reference resolution (pronouns, positional,
    temporal, object references), and ambiguity detection per (user_id, conversation_id).
    """

    def __init__(self):
        # Memory storage: f"{user_id}:{conversation_id}" -> ConversationContext
        self._contexts: Dict[str, ConversationContext] = {}

    def _get_key(self, user_id: str, conversation_id: str) -> str:
        clean_user = user_id or "user_guest"
        clean_conv = conversation_id or "default_session"
        return f"{clean_user}:{clean_conv}"

    def get_context(self, user_id: str, conversation_id: str) -> ConversationContext:
        """Retrieve existing conversation context or initialize a clean context for session."""
        key = self._get_key(user_id, conversation_id)
        if key not in self._contexts:
            self._contexts[key] = ConversationContext(
                user_id=user_id or "user_guest",
                conversation_id=conversation_id or "default_session",
                entities=EntityMemory()
            )
        return self._contexts[key]

    def clear_context(self, user_id: str, conversation_id: str) -> None:
        """Clear conversation context for session."""
        key = self._get_key(user_id, conversation_id)
        if key in self._contexts:
            del self._contexts[key]

    def resolve_context(
        self,
        user_id: str,
        conversation_id: str,
        query: str
    ) -> Tuple[str, bool, bool, Optional[str]]:
        """
        Resolves query references based on stored conversation context.
        Returns:
            resolved_query (str): Rewritten or enriched query string
            context_used (bool): Whether context was applied
            needs_clarification (bool): True if ambiguous reference requires user clarification
            clarification_message (Optional[str]): Clarification prompt to user if ambiguous
        """
        context = self.get_context(user_id, conversation_id)
        entities = context.entities
        query_lower = query.lower().strip()
        resolved_query = query
        context_used = False
        needs_clarification = False
        clarification_message = None

        if not query_lower:
            return query, False, False, None

        # 1. Check for Ambiguity when referring to faculty
        # E.g. "when is his class?" or "where is his office?" when multiple faculty candidates exist
        is_faculty_ref = any(p in query_lower for p in ["his ", "his?", "her ", "her?", "he ", "she ", "the professor", "the teacher", "the faculty"])
        if is_faculty_ref:
            candidates = entities.candidate_faculty
            if len(candidates) > 1 and not entities.faculty:
                names = [c.get("name") or c.get("Name") for c in candidates if c.get("name") or c.get("Name")]
                if len(names) > 1:
                    needs_clarification = True
                    clarification_message = f"Which faculty member do you mean? ({', '.join(names[:3])})"
                    return query, False, True, clarification_message

        # 2. Faculty / Pronoun Reference Resolution
        if is_faculty_ref and entities.faculty:
            fac_name = entities.faculty.get("name") or entities.faculty.get("Name") or "faculty"
            # Replace pronouns with faculty name
            new_q = re.sub(r"\b(his|her|he|she)\b", fac_name, query, flags=re.IGNORECASE)
            new_q = re.sub(r"\b(the professor|the teacher|the faculty)\b", fac_name, new_q, flags=re.IGNORECASE)
            if new_q != query:
                resolved_query = new_q
                context_used = True

        # 3. Positional Reference Resolution ("first one", "second one", "1st subject", etc.)
        pos_match = re.search(r"\b(first|1st|second|2nd|third|3rd)\s*(one|subject|course|event|workshop)?\b", query_lower)
        if pos_match:
            pos_term = pos_match.group(1)
            idx = 0 if pos_term in ["first", "1st"] else 1 if pos_term in ["second", "2nd"] else 2

            # Check if query targets subjects
            if any(k in query_lower for k in ["subject", "course", "credit", "credits", "syllabus", "unit", "have"]):
                subjects_pool = entities.last_subjects or ([entities.subject] if entities.subject else [])
                if subjects_pool and len(subjects_pool) > idx and subjects_pool[idx]:
                    subj_item = subjects_pool[idx]
                    subj_name = subj_item.get("Subjects") or subj_item.get("name") or subj_item.get("subject") or "subject"
                    if isinstance(subj_name, str) and "|" in subj_name:
                        parts = [p.strip() for p in subj_name.split("|") if p.strip()]
                        subj_name = parts[idx] if idx < len(parts) else parts[0]
                    resolved_query = re.sub(r"\b(the\s+)?(first|1st|second|2nd|third|3rd)\s*(one|subject|course)?\b", f"'{subj_name}'", query, flags=re.IGNORECASE)
                    context_used = True
            # Check if query targets events
            elif any(k in query_lower for k in ["event", "workshop", "hackathon", "register", "more", "tell me"]):
                events_pool = entities.last_events or ([entities.event] if entities.event else [])
                if events_pool and len(events_pool) > idx and events_pool[idx]:
                    evt_item = events_pool[idx]
                    evt_title = evt_item.get("title") or evt_item.get("Event_Name") or "event"
                    resolved_query = re.sub(r"\b(the\s+)?(first|1st|second|2nd|third|3rd)\s*(one|event|workshop|hackathon)?\b", f"'{evt_title}'", query, flags=re.IGNORECASE)
                    context_used = True

        # 4. Event Registration Intent ("Register me for it", "Sign me up", "Register for it")
        if any(k in query_lower for k in ["register me", "sign me up", "register for it", "register for this"]):
            target_evt = entities.event or (entities.last_events[0] if entities.last_events else None)
            if target_evt:
                evt_title = target_evt.get("title") or target_evt.get("Event_Name") or "event"
                evt_id = target_evt.get("id") or target_evt.get("Event_ID") or ""
                resolved_query = f"Register user for event '{evt_title}' (ID: {evt_id})"
                context_used = True

        # 5. Object Reference Resolution ("it", "this", "that")
        if not context_used and any(w in query_lower.split() for w in ["it", "this", "that"]):
            if entities.event and any(k in query_lower for k in ["event", "workshop", "register", "about"]):
                evt_title = entities.event.get("title") or entities.event.get("Event_Name") or ""
                if evt_title:
                    resolved_query = re.sub(r"\b(it|this|that)\b", f"'{evt_title}'", query, flags=re.IGNORECASE)
                    context_used = True
            elif entities.subject and any(k in query_lower for k in ["subject", "credits", "credit", "syllabus"]):
                subj_name = entities.subject.get("name") or entities.subject.get("Subjects") or ""
                if subj_name:
                    resolved_query = re.sub(r"\b(it|this|that)\b", f"'{subj_name}'", query, flags=re.IGNORECASE)
                    context_used = True

        # 6. Temporal Reference Resolution ("today", "tomorrow", "yesterday", "this week")
        now = datetime.datetime.now()
        if "today" in query_lower:
            today_str = now.strftime("%Y-%m-%d")
            resolved_query = resolved_query.replace("today", f"today ({today_str})")
            context_used = True
        elif "tomorrow" in query_lower:
            tomorrow_str = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            resolved_query = resolved_query.replace("tomorrow", f"tomorrow ({tomorrow_str})")
            context_used = True

        # 7. Inherit Academic/Branch/Semester Filters if follow-up is academic
        if not context_used and any(k in query_lower for k in ["subjects", "syllabus", "credits", "next class"]):
            if entities.semester or entities.branch:
                additions = []
                if entities.branch and entities.branch.lower() not in query_lower:
                    additions.append(entities.branch)
                if entities.semester and entities.semester.lower() not in query_lower:
                    additions.append(f"Sem {entities.semester}")
                if additions:
                    resolved_query = f"{resolved_query} ({' '.join(additions)})"
                    context_used = True

        logger.info(f"[ContextResolver] Raw: '{query}' -> Resolved: '{resolved_query}' (Context Used: {context_used})")
        return resolved_query, context_used, needs_clarification, clarification_message

    def update_context(
        self,
        user_id: str,
        conversation_id: str,
        query: str,
        agents_used: List[str],
        agent_results: Dict[str, Any],
        final_answer: str
    ) -> ConversationContext:
        """
        Updates stored conversation context with newly discovered entities from current turn execution.
        """
        context = self.get_context(user_id, conversation_id)
        entities = context.entities
        context.turns_count += 1
        context.last_agents = agents_used
        if agents_used:
            context.last_agent = agents_used[0]

        # Extract entities from agent_results data payloads
        for agent_name, res in agent_results.items():
            if not res or not getattr(res, "success", False):
                continue

            res_data = getattr(res, "data", None)
            if not isinstance(res_data, dict):
                continue

            # 1. Faculty entity extraction
            if "faculty_profile" in res_data and isinstance(res_data["faculty_profile"], dict):
                fac = res_data["faculty_profile"]
                entities.faculty = {
                    "name": fac.get("Name"),
                    "id": fac.get("Faculty ID"),
                    "department": fac.get("Department") or fac.get("Qualification")
                }
                entities.candidate_faculty = [entities.faculty]
            elif "faculty" in res_data and isinstance(res_data["faculty"], str):
                entities.faculty = {"name": res_data["faculty"]}
                entities.candidate_faculty = [entities.faculty]

            # 2. Academic / Subject / Student extraction
            if "subjects" in res_data or "student_name" in res_data:
                if res_data.get("roll_no"): entities.roll_no = res_data.get("roll_no")
                if res_data.get("branch"): entities.branch = res_data.get("branch")
                if res_data.get("sem"): entities.semester = res_data.get("sem")

            if "sample" in res_data and isinstance(res_data["sample"], dict):
                s = res_data["sample"]
                subj_name = s.get("Subjects") or s.get("subjects")
                subj_obj = {"name": subj_name, "Subjects": subj_name, "credits": s.get("Credits")}
                entities.subject = subj_obj
                entities.last_subjects = [subj_obj]
                if s.get("Branch"): entities.branch = s.get("Branch")
                if s.get("Semester"): entities.semester = s.get("Semester")
            elif "academic_record" in res_data and isinstance(res_data["academic_record"], dict):
                rec = res_data["academic_record"]
                subj_name = rec.get("Subjects") or rec.get("subjects")
                if subj_name:
                    subj_obj = {"name": subj_name, "Subjects": subj_name, "credits": rec.get("Credits")}
                    entities.subject = subj_obj
                    entities.last_subjects = [subj_obj]
                if rec.get("Branch"): entities.branch = rec.get("Branch")
                if rec.get("Semester"): entities.semester = rec.get("Semester")

            # 3. Events extraction
            if "events" in res_data and isinstance(res_data["events"], list):
                entities.last_events = res_data["events"]
                if res_data["events"]:
                    e = res_data["events"][0]
                    if isinstance(e, dict):
                        entities.event = e
            elif "event" in res_data and isinstance(res_data["event"], dict):
                entities.event = res_data["event"]
                entities.last_events = [res_data["event"]]

            # 4. Timetable extraction
            if "schedule" in res_data and isinstance(res_data["schedule"], dict):
                entities.timetable = res_data["schedule"]

        context.entities = entities
        context.updated_at = datetime.datetime.now().isoformat()
        logger.info(f"[ContextService] Updated context for session '{conversation_id}' (Turn {context.turns_count})")
        return context
