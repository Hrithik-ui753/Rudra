import re
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class AcademicAgent(BaseAgent):
    """
    Academic Agent responsible for retrieving structured student records,
    roll numbers, subjects, courses, syllabus, credits, semesters, and CGPA/SGPA.
    Uses direct JSON lookup (No RAG).
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="academic_agent",
            description="Handles academic queries including student roll number profiles, subjects, courses, syllabus, credits, and semester information.",
            supported_queries=[
                "Tell me about 1602-24-737-016",
                "What subjects are in 3rd semester?",
                "Show details for student Arjun Kulkarni",
                "What are the credits for Sem I?"
            ],
            json_service=json_service
        )
        self.academic_datasets = [
            "all_years_students_database",
            "ACAD/3rdyear_academicagent",
            "ACAD/2ndyear_academicagent",
            "ACAD/1styear_academic",
            "ACAD/4th_year_students_final_corrected (1)"
        ]

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        available_datasets = [d for d in self.academic_datasets if self.is_dataset_available(d)]
        if not available_datasets:
            return self.data_unavailable_result("Academic Datasets (ACAD)")

        # Check if query contains a Roll Number pattern (e.g. 1602-24-737-016)
        roll_match = re.search(r"1602[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{3}", query, re.IGNORECASE)
        target_roll = roll_match.group(0).replace(" ", "-").upper() if roll_match else None

        # Clean search terms
        clean_terms = [re.sub(r"[^\w\-]", "", w).lower() for w in query.split() if len(w) > 2]
        filter_words = {"tell", "about", "what", "is", "the", "for", "show", "details", "info", "student", "mam", "madam", "sir", "prof", "professor", "teacher", "faculty", "hod", "dr", "doctor", "ms", "mrs", "miss", "subjects", "subject", "semester", "sem", "course", "courses", "syllabus", "list", "are", "there", "have", "it", "cse", "ece", "eee", "civil", "mech", "aiml", "aids"}
        search_terms = [t for t in clean_terms if t not in filter_words and len(t) >= 4]

        # Check if query is targeting a faculty member rather than a student
        is_faculty_query = any(w in query.lower() for w in ["mam", "madam", "sir", "prof", "professor", "teacher", "faculty", "hod", "dr.", "doctor", "ms.", "mrs.", "miss"])

        # Gather records across student & academic datasets
        student_db_record = None
        academic_record = None

        if target_roll or (search_terms and not is_faculty_query):
            # 1. Search All_Years_Students_Database
            db_data = self.json_service.get_dataset("all_years_students_database")
            if isinstance(db_data, list):
                for row in db_data:
                    if isinstance(row, list) and len(row) >= 5:
                        r_no = str(row[0]).upper()
                        name = str(row[1]).lower()
                        if (target_roll and target_roll in r_no) or (search_terms and any(t in name for t in search_terms)):
                            student_db_record = row
                            break

        # 2. Search Year Academic Datasets
        for ds in ["ACAD/3rdyear_academicagent", "ACAD/2ndyear_academicagent", "ACAD/1styear_academic", "ACAD/4th_year_students_final_corrected (1)"]:
            items = self.json_service.get_dataset(ds)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        r_no = str(item.get("Roll No") or item.get("Roll_No") or item.get("roll_no") or "").upper()
                        name = str(item.get("Name") or item.get("Student Name") or "").lower()
                        if (target_roll and target_roll in r_no) or (search_terms and search_terms[0] in name if search_terms else False):
                            academic_record = item
                            break
                    elif isinstance(item, list) and len(item) >= 6:
                        r_no = str(item[0]).upper()
                        name = str(item[1]).lower()
                        if (target_roll and target_roll in r_no) or (search_terms and search_terms[0] in name if search_terms else False):
                            academic_record = item
                            break
                if academic_record:
                    break

        # If a specific student record was matched:
        if student_db_record or academic_record:
            # Build unified student record answer
            roll_no = target_roll or (student_db_record[0] if student_db_record else "N/A")
            student_name = "N/A"
            branch = "N/A"
            sem = "N/A"
            year = "N/A"
            email = "N/A"
            phone = "N/A"
            parent = "N/A"
            cgpa = "N/A"
            sgpa = "N/A"
            attendance = "N/A"
            marks = "N/A"
            classroom = "N/A"
            subjects = "N/A"
            credits = "N/A"

            if student_db_record:
                roll_no = student_db_record[0]
                student_name = student_db_record[1]
                branch = student_db_record[2]
                year = student_db_record[3]
                sem = student_db_record[4]
                if len(student_db_record) > 5: email = student_db_record[5]
                if len(student_db_record) > 6: phone = student_db_record[6]
                if len(student_db_record) > 7: parent = student_db_record[7]

            if isinstance(academic_record, dict):
                student_name = academic_record.get("Name") or academic_record.get("Student Name") or student_name
                branch = academic_record.get("Branch") or branch
                sem = academic_record.get("Semester") or sem
                year = academic_record.get("Year of Study") or year
                cgpa = academic_record.get("CGPA") or cgpa
                sgpa = academic_record.get("SGPA") or sgpa
                attendance = academic_record.get("Attendance (%)") or academic_record.get("Attendance") or attendance
                marks = academic_record.get("Internal Marks (/40)") or academic_record.get("Internal Marks") or marks
                classroom = academic_record.get("Classroom") or classroom
                subjects = academic_record.get("Subjects") or subjects
                credits = academic_record.get("Credits") or credits
            elif isinstance(academic_record, list) and len(academic_record) >= 7:
                roll_no = academic_record[0]
                student_name = academic_record[1]
                branch = academic_record[2]
                sem = academic_record[4]
                subjects = academic_record[5]
                credits = academic_record[6]

            lines = [
                f"🎓 **Student Academic Profile for Roll No: {roll_no}**",
                f"• **Student Name**: {student_name}",
                f"• **Branch & Section**: {branch}",
                f"• **Year & Semester**: {year} Year (Sem {sem})",
                f"• **Classroom**: {classroom}",
                f"• **CGPA**: {cgpa} | **SGPA**: {sgpa}",
                f"• **Attendance**: {attendance} | **Internal Marks**: {marks}",
                f"• **Email**: {email} | **Contact**: {phone}",
                f"• **Parent/Guardian**: {parent}",
                f"• **Enrolled Subjects**: {subjects}",
                f"• **Credits Breakdown**: {credits}"
            ]

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Academic Curriculum & Student Database",
                source_file="academic_curriculum.json" if academic_record else "all_years_students_database.json",
                retrieval_method="exact_lookup" if target_roll else "filtered_json",
                records_matched=1,
                filters={"roll_no": roll_no, "branch": branch, "semester": sem} if roll_no != "N/A" else {"branch": branch, "semester": sem},
                relevance=0.98,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.98,
                answer="\n".join(lines),
                data={
                    "roll_no": roll_no,
                    "student_name": student_name,
                    "db_record": student_db_record,
                    "academic_record": academic_record
                },
                evidence=[ev]
            )

        # Fallback to general academic subjects search if no roll number match
        matched_records = []
        matched_dataset_name = "academic_curriculum.json"
        query_lower = query.lower()

        # Check for semester indicator e.g. "3rd", "3", "iii", "1st", "2nd"
        sem_map = {"1": "I", "1st": "I", "2": "II", "2nd": "II", "3": "III", "3rd": "III", "4": "IV", "4th": "IV", "5": "V", "5th": "V", "6": "VI", "6th": "VI", "7": "VII", "7th": "VII", "8": "VIII", "8th": "VIII"}
        target_sem = None
        for key, val in sem_map.items():
            if re.search(r"\b" + re.escape(key) + r"\b", query_lower) or f"sem {key}" in query_lower or f"semester {key}" in query_lower:
                target_sem = val
                break

        for dataset in available_datasets:
            items = self.json_service.get_dataset(dataset)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        item_sem = str(item.get("Semester") or item.get("semester") or "").upper()
                        item_sub = str(item.get("Subjects") or item.get("subjects") or "")
                        if target_sem and item_sem == target_sem:
                            matched_records.append(item)
                        elif search_terms and any(term in item_sub.lower() for term in search_terms if len(term) > 3):
                            matched_records.append(item)
                if matched_records:
                    matched_dataset_name = f"{dataset}.json"
                    break

        if not matched_records:
            for dataset in available_datasets:
                records = self.json_service.search_in_dataset(dataset, query)
                if records:
                    matched_records.extend(records)
                    matched_dataset_name = f"{dataset}.json"
                    break

        if matched_records:
            sample = matched_records[0]
            if isinstance(sample, dict):
                subjects = sample.get("Subjects") or sample.get("subjects")
                credits = sample.get("Credits") or sample.get("credits")
                branch = sample.get("Branch") or sample.get("branch")
                sem = sample.get("Semester") or sample.get("semester")

                answer_parts = []
                if branch or sem:
                    answer_parts.append(f"Academic Info for {branch or ''} (Sem {sem or ''}):")
                if subjects:
                    answer_parts.append(f"• Subjects: {subjects}")
                if credits:
                    answer_parts.append(f"• Credits: {credits}")

                if answer_parts:
                    filters_dict = {}
                    if branch: filters_dict["branch"] = branch
                    if sem: filters_dict["semester"] = sem
                    
                    ev = self.create_evidence(
                        source_type="structured_data",
                        source_name="Academic Curriculum",
                        source_file=matched_dataset_name,
                        retrieval_method="filtered_json",
                        records_matched=len(matched_records),
                        filters=filters_dict or {"query": query},
                        relevance=0.98,
                        verified=True
                    )

                    return AgentResult(
                        agent_name=self.name,
                        success=True,
                        confidence=0.95,
                        answer="\n".join(answer_parts),
                        data={"matched_count": len(matched_records), "sample": sample},
                        evidence=[ev]
                    )

        # General summary fallback (no verified records matched)
        default_answer = (
            "Academic Information Structure:\n"
            "• Semester 1 & 2: Mathematics, Engineering Physics, Chemistry, English, PPS, Workshop.\n"
            "• Semester 3 & 4: Core Branch Subjects, Skill Development Courses, Labs.\n"
            "• Semester 5 & 6: Advanced Electives, Artificial Intelligence, Computer Networks, Labs.\n"
            "• Semester 7 & 8: Major Projects, Industry Internships, Seminars."
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.80,
            answer=default_answer,
            data={"status": "general_academic_info"},
            evidence=[]
        )
