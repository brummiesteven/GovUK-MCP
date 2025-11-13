"""Parliamentary questions search tool."""
import requests
from datetime import datetime
from gov_uk_mcp.validation import sanitize_api_error


QUESTIONS_API_URL = "https://questions-statements-api.parliament.uk/api"


def search_questions(query, mp_name=None, department=None, limit=20):
    """Search parliamentary written questions.

    Args:
        query: Search term
        mp_name: Filter by MP name (optional)
        department: Filter by answering department (optional)
        limit: Number of results to return
    """
    mp_id = None
    if mp_name:
        from gov_uk_mcp.tools.mps import find_mp

        mp_result = find_mp(mp_name)
        if "error" in mp_result:
            return mp_result

        if "mps" in mp_result:
            return {"error": "Multiple MPs found. Please be more specific."}

        mp_id = mp_result.get("id")

    try:
        params = {
            "searchTerm": query,
            "take": limit,
            "skip": 0
        }

        if mp_id:
            params["askingMemberId"] = mp_id

        if department:
            params["answeringBodyName"] = department

        response = requests.get(
            f"{QUESTIONS_API_URL}/writtenquestions/questions",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        if not results:
            return {"message": "No questions found matching your search"}

        questions = []
        for q in results:
            questions.append({
                "id": q.get("value", {}).get("id"),
                "date_tabled": q.get("value", {}).get("dateTabled"),
                "question_text": q.get("value", {}).get("questionText"),
                "asking_member": q.get("value", {}).get("askingMemberPrinted"),
                "answering_body": q.get("value", {}).get("answeringBodyName"),
                "answer_text": q.get("value", {}).get("answerText"),
                "answer_date": q.get("value", {}).get("dateAnswered"),
                "uin": q.get("value", {}).get("uin")
            })

        return {
            "query": query,
            "total_results": data.get("totalResults"),
            "showing": len(questions),
            "questions": questions,
            "data_source": "Parliamentary Questions API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_question_by_id(question_id):
    """Get details of a specific parliamentary question."""
    try:
        response = requests.get(
            f"{QUESTIONS_API_URL}/writtenquestions/questions/{question_id}",
            timeout=10
        )

        if response.status_code == 404:
            return {"error": "Question not found"}

        response.raise_for_status()
        data = response.json()
        q = data.get("value", {})

        return {
            "id": q.get("id"),
            "uin": q.get("uin"),
            "date_tabled": q.get("dateTabled"),
            "question_text": q.get("questionText"),
            "asking_member": q.get("askingMemberPrinted"),
            "asking_member_constituency": q.get("askingMemberConstituency"),
            "answering_body": q.get("answeringBodyName"),
            "answer_text": q.get("answerText"),
            "answer_date": q.get("dateAnswered"),
            "is_withdrawn": q.get("isWithdrawn"),
            "data_source": "Parliamentary Questions API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)


def get_questions_by_mp(mp_name, limit=20):
    """Get all questions asked by a specific MP."""
    from gov_uk_mcp.tools.mps import find_mp

    mp_result = find_mp(mp_name)
    if "error" in mp_result:
        return mp_result

    if "mps" in mp_result:
        return {"error": "Multiple MPs found. Please be more specific."}

    mp_id = mp_result.get("id")
    mp_name_display = mp_result.get("name")

    try:
        response = requests.get(
            f"{QUESTIONS_API_URL}/writtenquestions/questions",
            params={"askingMemberId": mp_id, "take": limit, "skip": 0},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        if not results:
            return {"message": f"No questions found from {mp_name_display}"}

        questions = []
        for q in results:
            questions.append({
                "id": q.get("value", {}).get("id"),
                "date_tabled": q.get("value", {}).get("dateTabled"),
                "question_text": q.get("value", {}).get("questionText"),
                "answering_body": q.get("value", {}).get("answeringBodyName"),
                "answer_text": q.get("value", {}).get("answerText"),
                "answer_date": q.get("value", {}).get("dateAnswered"),
                "uin": q.get("value", {}).get("uin")
            })

        return {
            "mp_name": mp_name_display,
            "mp_id": mp_id,
            "total_results": data.get("totalResults"),
            "showing": len(questions),
            "questions": questions,
            "data_source": "Parliamentary Questions API",
            "retrieved_at": datetime.now().isoformat()
        }

    except (requests.Timeout, requests.RequestException, requests.HTTPError) as e:
        return sanitize_api_error(e)
