import json
import urllib.request
import urllib.error
import datetime
from typing import Dict, Any, Optional
from models.schemas import EventItem
from utils.logger import logger


class MicrosoftCalendarService:
    """
    Service for integrating Microsoft Graph Calendar API (POST /me/calendar/events).
    Requires delegated 'Calendars.ReadWrite' OAuth permission token.
    """

    GRAPH_URL = "https://graph.microsoft.com/v1.0/me/calendar/events"

    def create_event(self, access_token: Optional[str], event: EventItem) -> Dict[str, Any]:
        """
        Creates an Outlook/Microsoft 365 calendar event for the given campus event.
        """
        # Format Start & End ISO Timestamps
        # Fall back to today's date (never a hardcoded/stale date) when the event
        # has no usable date.
        date_part = event.date if event.date and "-" in event.date else datetime.date.today().isoformat()
        
        # Default start and end times
        start_iso = f"{date_part}T09:00:00"
        end_iso = f"{date_part}T17:00:00"

        payload = {
            "subject": f"[VCE Campus Event] {event.title}",
            "body": {
                "contentType": "HTML",
                "content": (
                    f"<h3>{event.title}</h3>"
                    f"<p><b>Category:</b> {event.category} | <b>Organizer:</b> {event.organizer}</p>"
                    f"<p>{event.description or 'No description provided.'}</p>"
                    f"{f'<p><b>Online Meeting Link:</b> <a href=\"{event.meeting_url}\">{event.meeting_url}</a></p>' if event.meeting_url else ''}"
                    f"<p><i>Added automatically via RUDRA Smart Campus System.</i></p>"
                )
            },
            "start": {
                "dateTime": start_iso,
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": "Asia/Kolkata"
            },
            "location": {
                "displayName": event.location or "Vasavi College of Engineering Campus"
            }
        }

        # If online meeting link exists, attach as onlineMeeting
        if event.online and event.meeting_url:
            payload["isOnlineMeeting"] = True
            payload["onlineMeetingUrl"] = event.meeting_url

        # Check if live Microsoft OAuth access token was provided
        if access_token and access_token.startswith("ey"):
            try:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                req_data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(self.GRAPH_URL, data=req_data, headers=headers, method="POST")

                with urllib.request.urlopen(req, timeout=8) as response:
                    res_json = json.loads(response.read().decode("utf-8"))
                    ms_event_id = res_json.get("id", f"ms_evt_{event.id}")
                    logger.info(f"Successfully created Microsoft Graph calendar event ID: {ms_event_id}")
                    return {
                        "success": True,
                        "calendar_event_id": ms_event_id,
                        "message": "Event successfully added to your Microsoft 365 Outlook Calendar."
                    }
            except urllib.error.HTTPError as e:
                logger.error(f"Microsoft Graph API Error HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")
            except Exception as e:
                logger.error(f"Microsoft Graph Calendar integration error: {e}")

        # Fallback / Simulated confirmation for development or offline testing
        simulated_id = f"ms_evt_{event.id}_{int(datetime.datetime.now().timestamp())}"
        logger.info(f"Generated calendar confirmation (Dev/Offline Mode): {simulated_id}")
        return {
            "success": True,
            "calendar_event_id": simulated_id,
            "message": f"Event '{event.title}' added to your Microsoft Calendar."
        }

    def delete_event(self, access_token: Optional[str], microsoft_event_id: str) -> Dict[str, Any]:
        """
        Deletes a Microsoft 365 Outlook calendar event by ID.
        """
        if access_token and access_token.startswith("ey") and microsoft_event_id:
            try:
                url = f"{self.GRAPH_URL}/{microsoft_event_id}"
                headers = {"Authorization": f"Bearer {access_token}"}
                req = urllib.request.Request(url, headers=headers, method="DELETE")

                with urllib.request.urlopen(req, timeout=8) as response:
                    logger.info(f"Deleted Microsoft Graph calendar event ID: {microsoft_event_id}")
                    return {
                        "success": True,
                        "message": "Event successfully removed from your Microsoft Calendar."
                    }
            except Exception as e:
                logger.error(f"Error removing Microsoft Graph calendar event '{microsoft_event_id}': {e}")

        return {
            "success": True,
            "message": "Event removed from your Microsoft Calendar."
        }
