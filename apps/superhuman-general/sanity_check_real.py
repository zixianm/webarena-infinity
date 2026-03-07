#!/usr/bin/env python3
"""
Sanity check for Superhuman Mail real tasks.

For each task, directly applies the expected end-state (bypassing the agent),
then runs the verifier and asserts it passes.

Usage:
    python3 sanity_check_real.py                     # All tasks, sequential
    python3 sanity_check_real.py --workers N          # N parallel environments
    python3 sanity_check_real.py --task-id task_e1    # Single task
    python3 sanity_check_real.py --port 9500          # Custom base port
"""
import argparse
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "real-tasks.json"

# JS snippet to evaluate data.js and emit the seed state as JSON
_SEED_STATE_JS = """
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
vm.runInThisContext(code);

const state = {
    _seedVersion: SEED_DATA_VERSION,
    emails: JSON.parse(JSON.stringify(EMAILS)),
    contacts: JSON.parse(JSON.stringify(CONTACTS)),
    labels: JSON.parse(JSON.stringify(LABELS)),
    autoLabels: JSON.parse(JSON.stringify(AUTO_LABELS)),
    splits: JSON.parse(JSON.stringify(SPLITS)),
    snippets: JSON.parse(JSON.stringify(SNIPPETS)),
    calendarEvents: JSON.parse(JSON.stringify(CALENDAR_EVENTS)),
    settings: JSON.parse(JSON.stringify(SETTINGS)),
    currentUser: JSON.parse(JSON.stringify(CURRENT_USER)),
    recentOpens: JSON.parse(JSON.stringify(RECENT_OPENS)),
    bookingPages: JSON.parse(JSON.stringify(BOOKING_PAGES)),
    _nextEmailId: EMAILS.length > 0 ? Math.max(...EMAILS.map(e => e.id)) + 1 : 200,
    _nextLabelId: 30,
    _nextSnippetId: 30,
    _nextEventId: 30,
    _nextAutoLabelId: 20,
    _nextSplitId: 20,
    _nextBookingPageId: 10,
};
process.stdout.write(JSON.stringify(state));
"""


# -- helpers ------------------------------------------------------------------

def find_email(state, subject, sender_email=None):
    for e in state["emails"]:
        if e["subject"] == subject:
            if sender_email is None or e["from"]["email"] == sender_email:
                return e
    raise ValueError(f"Email not found: subject={subject!r}, from={sender_email!r}")


def find_email_contains(state, substring, sender_email=None):
    for e in state["emails"]:
        if substring in e["subject"]:
            if sender_email is None or e["from"]["email"] == sender_email:
                return e
    raise ValueError(f"Email not found containing: {substring!r}")


def find_label(state, name):
    for l in state["labels"]:
        if l["name"] == name:
            return l
    raise ValueError(f"Label not found: {name!r}")


def find_snippet(state, name):
    for s in state["snippets"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Snippet not found: {name!r}")


def find_event(state, title):
    for e in state["calendarEvents"]:
        if e["title"] == title:
            return e
    raise ValueError(f"Event not found: {title!r}")


def find_booking_page(state, title):
    for b in state["bookingPages"]:
        if b["title"] == title:
            return b
    raise ValueError(f"Booking page not found: {title!r}")


def find_auto_label(state, name):
    for a in state["autoLabels"]:
        if a["name"] == name:
            return a
    raise ValueError(f"Auto label not found: {name!r}")


def find_split(state, name):
    for s in state["splits"]:
        if s["name"] == name:
            return s
    raise ValueError(f"Split not found: {name!r}")


def inbox_emails(state):
    """Return emails that are in the inbox (not done, trashed, spam, draft, or reminded)."""
    return [e for e in state["emails"]
            if not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
            and not e["isDraft"] and not e.get("remindAt")]


# -- solve functions ----------------------------------------------------------

# === EASY ===

def solve_task_e1(state):
    """Switch to dark mode."""
    state["settings"]["theme"] = "dark"


def solve_task_e2(state):
    """Turn off desktop notifications."""
    state["settings"]["notifications"]["desktop"] = False


def solve_task_e3(state):
    """Disable sound notifications."""
    state["settings"]["notifications"]["sound"] = False


def solve_task_e4(state):
    """Star the email from David Kim about the FinancePlus partnership."""
    email = find_email(state, "Partnership Opportunity - FinancePlus x Acme", "david.kim@financeplus.com")
    email["isStarred"] = True


def solve_task_e5(state):
    """Archive Sarah Chen's email about the Q2 roadmap."""
    email = find_email(state, "Q2 Product Roadmap - Final Review", "sarah.chen@acmecorp.com")
    email["isDone"] = True
    email["isRead"] = True
    email["remindAt"] = None


def solve_task_e6(state):
    """Trash the email about office equipment delivery from Carlos."""
    email = find_email(state, "Logistics Update - Office Equipment Delivery", "carlos.m@logisticspro.net")
    email["isTrashed"] = True
    email["isDone"] = False
    email["remindAt"] = None


def solve_task_e7(state):
    """Delete the 'Decline Politely' snippet."""
    state["snippets"] = [s for s in state["snippets"] if s["name"] != "Decline Politely"]


def solve_task_e8(state):
    """Turn off Instant Reply."""
    state["settings"]["instantReply"]["enabled"] = False


def solve_task_e9(state):
    """Disable Smart Send."""
    state["settings"]["smartSend"]["enabled"] = False


def solve_task_e10(state):
    """Turn off read receipts."""
    state["settings"]["readReceipts"]["enabled"] = False


def solve_task_e11(state):
    """Remove the Feeds split from the inbox."""
    state["splits"] = [s for s in state["splits"] if s["name"] != "Feeds"]


def solve_task_e12(state):
    """Activate the Quick Sync booking page."""
    bp = find_booking_page(state, "Quick Sync")
    bp["isActive"] = True


def solve_task_e13(state):
    """Delete the Product Demo booking page."""
    state["bookingPages"] = [b for b in state["bookingPages"] if b["title"] != "Product Demo"]


def solve_task_e14(state):
    """Turn off keyboard shortcuts."""
    state["settings"]["keyboard"]["shortcuts"] = False


def solve_task_e15(state):
    """Enable the Shipping Update auto label."""
    al = find_auto_label(state, "Shipping Update")
    al["enabled"] = True


def solve_task_e16(state):
    """Cancel the Yoga Class event."""
    state["calendarEvents"] = [e for e in state["calendarEvents"]
                                if not (e["title"] == "Yoga Class" and e["date"] == "2026-03-07")]


def solve_task_e17(state):
    """Disable auto archive."""
    state["settings"]["autoArchive"]["enabled"] = False


def solve_task_e18(state):
    """Switch the meeting link provider to Google Meet."""
    state["settings"]["meetingLink"]["provider"] = "google-meet"


def solve_task_e19(state):
    """Set the swipe left action to Trash."""
    state["settings"]["swipeLeft"] = "trash"


def solve_task_e20(state):
    """Disable the Team Update auto label."""
    al = find_auto_label(state, "Team Update")
    al["enabled"] = False


# === MEDIUM ===

def solve_task_m1(state):
    """Label the FinancePlus partnership email with Finance and Clients."""
    email = find_email(state, "Partnership Opportunity - FinancePlus x Acme", "david.kim@financeplus.com")
    finance = find_label(state, "Finance")
    clients = find_label(state, "Clients")
    for lid in [finance["id"], clients["id"]]:
        if lid not in email["labels"]:
            email["labels"].append(lid)


def solve_task_m2(state):
    """Create a new label called 'Partnerships' with a blue color."""
    next_id = state.get("_nextLabelId", 30)
    state["labels"].append({
        "id": f"label_{next_id}",
        "name": "Partnerships",
        "type": "user",
        "color": "#2196F3",
    })
    state["_nextLabelId"] = next_id + 1


def solve_task_m3(state):
    """Share the 'Scheduling Request' snippet with the team."""
    snippet = find_snippet(state, "Scheduling Request")
    snippet["isShared"] = True


def solve_task_m4(state):
    """Send an email to Emily Rodriguez about scheduling a term sheet call."""
    next_id = state.get("_nextEmailId", 200)
    state["emails"].insert(0, {
        "id": next_id,
        "threadId": f"thread_{next_id + 1}",
        "from": {"name": state["currentUser"]["name"], "email": state["currentUser"]["email"]},
        "to": [{"name": "Emily Rodriguez", "email": "emily.r@venturelabs.co"}],
        "cc": [], "bcc": [],
        "subject": "Re: Series B Term Sheet Discussion",
        "snippet": "Let's schedule a call this Thursday to discuss the term sheet.",
        "body": "Hi Emily,\n\nLet's schedule a call this Thursday to discuss the term sheet details.\n\nBest,\nAlex",
        "date": "2026-03-07T12:00:00.000Z",
        "isRead": True, "isStarred": False, "isDone": False, "isTrashed": False,
        "isSpam": False, "isDraft": False, "labels": [],
        "hasAttachments": False, "attachments": [],
        "splitCategory": "important", "remindAt": None,
        "readReceipt": {"opened": False}, "autoLabel": None,
        "replyDraftingTeammate": None, "threadMessages": None,
    })
    state["_nextEmailId"] = next_id + 1


def solve_task_m5(state):
    """Set a reminder on the budget approval email from Priya."""
    email = find_email(state, "Budget Approval Needed - Marketing Campaign", "priya.sharma@acmecorp.com")
    email["remindAt"] = "2026-03-14T09:00:00.000Z"
    email["isRead"] = True


def solve_task_m6(state):
    """Unsubscribe from GitHub notifications."""
    # Find a GitHub email and mark it done
    for e in state["emails"]:
        if e["from"]["email"] == "notifications@github.com" and not e["isDone"]:
            e["isDone"] = True
            e["isRead"] = True
            break
    if "blockedSenders" not in state["settings"]:
        state["settings"]["blockedSenders"] = []
    if "notifications@github.com" not in state["settings"]["blockedSenders"]:
        state["settings"]["blockedSenders"].append("notifications@github.com")


def solve_task_m7(state):
    """Change the calendar alert timing to 30 minutes."""
    state["settings"]["notifications"]["alertMinutes"] = 30


def solve_task_m8(state):
    """Switch the auto-reminder mode to external."""
    state["settings"]["autoReminders"]["mode"] = "external"


def solve_task_m9(state):
    """Create a new snippet called 'Investor Update'."""
    next_id = state.get("_nextSnippetId", 30)
    state["snippets"].append({
        "id": f"snip_{next_id}",
        "name": "Investor Update",
        "body": "Hi {first_name},\n\nHere is our {quarter} investor update. Key highlights:\n\n{highlights}\n\nBest,\nAlex",
        "variables": ["first_name", "quarter", "highlights"],
        "isShared": False,
        "author": state["currentUser"]["name"],
        "authorId": state["currentUser"]["id"],
        "createdAt": "2026-03-07T12:00:00.000Z",
        "metrics": {"sends": 0, "openRate": 0, "responseRate": 0},
    })
    state["_nextSnippetId"] = next_id + 1


def solve_task_m10(state):
    """Delete the 'Receipts' label."""
    label_id = "label_13"
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]
    for email in state["emails"]:
        email["labels"] = [l for l in email["labels"] if l != label_id]


def solve_task_m11(state):
    """Switch the primary timezone to Pacific Time."""
    state["settings"]["timezone"] = "America/Los_Angeles"


def solve_task_m12(state):
    """Remove the secondary timezone."""
    state["settings"]["secondaryTimezone"] = ""


def solve_task_m13(state):
    """Change the auto drafts type to scheduling mode."""
    state["settings"]["autoDrafts"]["type"] = "scheduling"


def solve_task_m14(state):
    """Create a calendar event for team lunch next Tuesday at noon."""
    next_id = state.get("_nextEventId", 30)
    state["calendarEvents"].append({
        "id": f"evt_{next_id}",
        "title": "Team Lunch",
        "date": "2026-03-10",
        "startTime": "12:00",
        "endTime": "13:00",
        "location": "Cafe Gratitude",
        "description": "",
        "attendees": [],
        "meetingLink": None,
        "isAllDay": False,
        "calendarId": "work",
        "organizer": state["currentUser"]["email"],
        "status": "confirmed",
        "color": "#6C4FF7",
    })
    state["_nextEventId"] = next_id + 1


def solve_task_m15(state):
    """Move the term sheet email back to inbox and mark unread."""
    email = find_email(state, "Re: Series B Term Sheet Discussion", "emily.r@venturelabs.co")
    email["isDone"] = False
    email["isTrashed"] = False
    email["isSpam"] = False
    email["remindAt"] = None
    email["isRead"] = False


def solve_task_m16(state):
    """Disable auto-adding meeting links."""
    state["settings"]["meetingLink"]["autoAdd"] = False


def solve_task_m17(state):
    """Create a custom auto label 'Design Review' for designhub.io."""
    next_id = state.get("_nextAutoLabelId", 20)
    state["autoLabels"].append({
        "id": f"al_{next_id}",
        "name": "Design Review",
        "type": "custom",
        "enabled": True,
        "criteria": {"from": "designhub.io"},
    })
    state["_nextAutoLabelId"] = next_id + 1


def solve_task_m18(state):
    """Delete the Support Ticket auto label."""
    state["autoLabels"] = [a for a in state["autoLabels"] if a["name"] != "Support Ticket"]


def solve_task_m19(state):
    """Set swipe right to Star and swipe left to Spam."""
    state["settings"]["swipeRight"] = "star"
    state["settings"]["swipeLeft"] = "spam"


def solve_task_m20(state):
    """Turn on Cc teammate for auto drafts."""
    state["settings"]["autoDrafts"]["ccTeammate"] = True


# === HARD ===

def solve_task_h1(state):
    """Archive all unread newsletter emails from the Other split."""
    for e in state["emails"]:
        if (not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
                and not e["isDraft"] and not e.get("remindAt")
                and e.get("splitCategory") == "other"
                and e.get("autoLabel") == "Newsletter"
                and not e["isRead"]):
            e["isDone"] = True
            e["isRead"] = True


def solve_task_h2(state):
    """Add 'Urgent' label to all unread emails in the Important split."""
    urgent_id = "label_5"
    for e in state["emails"]:
        if (not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
                and not e["isDraft"] and not e.get("remindAt")
                and e.get("splitCategory") == "important"
                and not e["isRead"]):
            if urgent_id not in e["labels"]:
                e["labels"].append(urgent_id)


def solve_task_h3(state):
    """Create a new inbox split 'Investors' matching Investor auto label."""
    next_id = state.get("_nextSplitId", 20)
    state["splits"].append({
        "id": f"split_{next_id}",
        "name": "Investors",
        "position": len(state["splits"]),
        "isDefault": False,
        "criteria": {"autoLabel": "Investor"},
    })
    state["_nextSplitId"] = next_id + 1


def solve_task_h4(state):
    """Move all PagerDuty alert emails to trash."""
    for e in state["emails"]:
        if e["from"]["email"] == "alerts@pagerduty.com":
            e["isTrashed"] = True
            e["isDone"] = False
            e["remindAt"] = None


def solve_task_h5(state):
    """Send email to Sophie Laurent confirming EuroDesign attendance."""
    next_id = state.get("_nextEmailId", 200)
    state["emails"].insert(0, {
        "id": next_id,
        "threadId": f"thread_{next_id + 1}",
        "from": {"name": state["currentUser"]["name"], "email": state["currentUser"]["email"]},
        "to": [{"name": "Sophie Laurent", "email": "sophie.l@eurodesign.fr"}],
        "cc": [], "bcc": [],
        "subject": "Re: EuroDesign Conference - Speaker Invitation",
        "snippet": "I'd be delighted to speak at EuroDesign Summit 2026. The keynote topic about scaling products sounds great.",
        "body": "Hi Sophie,\n\nI'd be delighted to speak at EuroDesign Summit 2026. The proposed keynote topic about building products that scale sounds great.\n\nLooking forward to it!\n\nBest,\nAlex",
        "date": "2026-03-07T12:00:00.000Z",
        "isRead": True, "isStarred": False, "isDone": False, "isTrashed": False,
        "isSpam": False, "isDraft": False, "labels": [],
        "hasAttachments": False, "attachments": [],
        "splitCategory": "important", "remindAt": None,
        "readReceipt": {"opened": False}, "autoLabel": None,
        "replyDraftingTeammate": None, "threadMessages": None,
    })
    state["_nextEmailId"] = next_id + 1


def solve_task_h6(state):
    """Clear reminder on patent filing email and add Urgent label."""
    email = find_email(state, "Patent Filing Deadline - April 15", "james.obrien@legalwise.com")
    email["remindAt"] = None
    urgent_id = "label_5"
    if urgent_id not in email["labels"]:
        email["labels"].append(urgent_id)


def solve_task_h7(state):
    """Mark all emails labeled 'Engineering' as done."""
    eng_id = "label_11"
    for e in state["emails"]:
        if eng_id in e["labels"]:
            e["isDone"] = True
            e["isRead"] = True


def solve_task_h8(state):
    """Unsubscribe from PagerDuty and Datadog alerts."""
    if "blockedSenders" not in state["settings"]:
        state["settings"]["blockedSenders"] = []
    for sender in ["alerts@pagerduty.com", "alerts@datadog.com"]:
        if sender not in state["settings"]["blockedSenders"]:
            state["settings"]["blockedSenders"].append(sender)
    # Mark related emails as done
    for e in state["emails"]:
        if e["from"]["email"] in ("alerts@pagerduty.com", "alerts@datadog.com"):
            e["isDone"] = True
            e["isRead"] = True


def solve_task_h9(state):
    """Update email signature to Chief Product Officer."""
    sig = state["settings"]["signature"]
    state["settings"]["signature"] = sig.replace("VP of Product", "Chief Product Officer")


def solve_task_h10(state):
    """Star all inbox emails from Acme Corp teammates."""
    for e in state["emails"]:
        if (not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
                and not e["isDraft"] and not e.get("remindAt")
                and e["from"]["email"].endswith("@acmecorp.com")):
            e["isStarred"] = True


def solve_task_h11(state):
    """Create booking page 'Office Hours'."""
    next_id = state.get("_nextBookingPageId", 10)
    state["bookingPages"].append({
        "id": f"bp_{next_id}",
        "title": "Office Hours",
        "duration": 60,
        "location": "Google Meet",
        "description": "",
        "availability": {
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "startTime": "14:00",
            "endTime": "17:00",
        },
        "link": "https://cal.superhuman.com/alex.morgan/office-hours",
        "isActive": True,
    })
    state["_nextBookingPageId"] = next_id + 1


def solve_task_h12(state):
    """Trash all spam emails."""
    for e in state["emails"]:
        if e["isSpam"]:
            e["isTrashed"] = True


def solve_task_h13(state):
    """Ensure board meeting event exists on March 10."""
    # Event evt_12 already exists with this data, so no change needed.
    # Verify it's there; if not, create it.
    exists = any(
        e["title"] == "Q1 Board Meeting" and e["date"] == "2026-03-10"
        for e in state["calendarEvents"]
    )
    if not exists:
        next_id = state.get("_nextEventId", 30)
        state["calendarEvents"].append({
            "id": f"evt_{next_id}",
            "title": "Q1 Board Meeting",
            "date": "2026-03-10",
            "startTime": "10:00",
            "endTime": "12:00",
            "location": "Acme HQ - Board Room",
            "description": "Quarterly board review and strategy session",
            "attendees": ["emily.r@venturelabs.co", "patrick.oneil@acmecorp.com"],
            "meetingLink": None,
            "isAllDay": False,
            "calendarId": "work",
            "organizer": state["currentUser"]["email"],
            "status": "confirmed",
            "color": "#E54D89",
        })
        state["_nextEventId"] = next_id + 1


def solve_task_h14(state):
    """Remove Marketing label from all emails and delete the label."""
    label_id = "label_12"
    for email in state["emails"]:
        email["labels"] = [l for l in email["labels"] if l != label_id]
    state["labels"] = [l for l in state["labels"] if l["id"] != label_id]


def solve_task_h15(state):
    """Disable all AI features."""
    state["settings"]["instantReply"]["enabled"] = False
    state["settings"]["smartSend"]["enabled"] = False
    state["settings"]["askAi"]["enabled"] = False
    state["settings"]["autoReminders"]["enabled"] = False


def solve_task_h16(state):
    """Send the EuroDesign draft."""
    for e in state["emails"]:
        if e["isDraft"] and any(t["email"] == "sophie.l@eurodesign.fr" for t in e.get("to", [])):
            e["isDraft"] = False
            break


def solve_task_h17(state):
    """Create snippet 'NDA Request' shared with team."""
    next_id = state.get("_nextSnippetId", 30)
    state["snippets"].append({
        "id": f"snip_{next_id}",
        "name": "NDA Request",
        "body": "Hi {recipient_name},\n\nWe'd like to establish a mutual NDA between Acme Corp and {company_name} before proceeding. Please review and sign the attached agreement.\n\nBest,\nAlex",
        "variables": ["recipient_name", "company_name"],
        "isShared": True,
        "author": state["currentUser"]["name"],
        "authorId": state["currentUser"]["id"],
        "createdAt": "2026-03-07T12:00:00.000Z",
        "metrics": {"sends": 0, "openRate": 0, "responseRate": 0},
    })
    state["_nextSnippetId"] = next_id + 1


def solve_task_h18(state):
    """Set theme to System, disable sound, set calendar alerts to 5 min."""
    state["settings"]["theme"] = "auto"
    state["settings"]["notifications"]["sound"] = False
    state["settings"]["notifications"]["alertMinutes"] = 5


def solve_task_h19(state):
    """Label all CloudScale emails with Legal label."""
    legal_id = "label_9"
    for e in state["emails"]:
        if "CloudScale" in e["subject"] or "cloudscale" in e["subject"].lower():
            if legal_id not in e["labels"]:
                e["labels"].append(legal_id)


def solve_task_h20(state):
    """Mark all calendar invite emails in inbox as done."""
    for e in state["emails"]:
        if (not e["isDone"] and not e["isTrashed"] and not e["isSpam"]
                and not e["isDraft"]
                and e.get("splitCategory") == "calendar"
                and e.get("autoLabel") == "Calendar Invite"):
            e["isDone"] = True
            e["isRead"] = True


def solve_task_h21(state):
    """Create 'VIP' label (red) and apply to all starred emails."""
    next_id = state.get("_nextLabelId", 30)
    label_id = f"label_{next_id}"
    state["labels"].append({
        "id": label_id,
        "name": "VIP",
        "type": "user",
        "color": "#F44336",
    })
    state["_nextLabelId"] = next_id + 1
    for e in state["emails"]:
        if e.get("isStarred", False):
            if label_id not in e["labels"]:
                e["labels"].append(label_id)


def solve_task_h22(state):
    """Archive read Other-split notifications, star unread ones."""
    # Originally unread notification emails in inbox Other split
    originally_unread_ids = {25, 26, 115}
    # Originally read notification emails in inbox Other split
    originally_read_ids = {27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 41, 43,
                           84, 85, 86, 88, 90, 92, 95, 96, 98, 100, 116}
    for e in state["emails"]:
        eid = e["id"]
        if eid in originally_read_ids:
            e["isDone"] = True
            e["isRead"] = True
        elif eid in originally_unread_ids:
            e["isStarred"] = True


def solve_task_h23(state):
    """Create auto label 'Legal Notices' + split 'Legal'."""
    al_id = state.get("_nextAutoLabelId", 20)
    state["autoLabels"].append({
        "id": f"al_{al_id}",
        "name": "Legal Notices",
        "type": "custom",
        "enabled": True,
        "criteria": {"from": "legalwise.com"},
    })
    state["_nextAutoLabelId"] = al_id + 1

    sp_id = state.get("_nextSplitId", 20)
    state["splits"].append({
        "id": f"split_{sp_id}",
        "name": "Legal",
        "position": len(state["splits"]),
        "isDefault": False,
        "criteria": {"autoLabel": "Legal Notices"},
    })
    state["_nextSplitId"] = sp_id + 1


def solve_task_h24(state):
    """Share all personal (user-authored) snippets."""
    user_id = state["currentUser"]["id"]
    for s in state["snippets"]:
        if s.get("authorId") == user_id:
            s["isShared"] = True


def solve_task_h25(state):
    """Set reminder on Important split inbox emails with attachments."""
    target_ids = {1, 5, 9, 10, 18, 22, 120}
    for e in state["emails"]:
        if e["id"] in target_ids:
            e["remindAt"] = "2026-03-09T09:00:00.000Z"
            e["isRead"] = True


def solve_task_h26(state):
    """Turn off read receipts, keyboard shortcuts, swipe right to archive."""
    state["settings"]["readReceipts"]["enabled"] = False
    state["settings"]["keyboard"]["shortcuts"] = False
    state["settings"]["swipeRight"] = "done"


def solve_task_h27(state):
    """Delete booking page with shortest duration (Quick Sync, 15 min)."""
    state["bookingPages"] = [b for b in state["bookingPages"]
                              if b["title"] != "Quick Sync"]


def solve_task_h28(state):
    """Apply Finance label to all Priya Sharma emails."""
    finance_id = "label_3"
    for e in state["emails"]:
        if e["from"]["email"] == "priya.sharma@acmecorp.com":
            if finance_id not in e["labels"]:
                e["labels"].append(finance_id)


def solve_task_h29(state):
    """Change location of event with most attendees to Main Auditorium."""
    evt = max(state["calendarEvents"],
              key=lambda e: len(e.get("attendees", [])))
    evt["location"] = "Main Auditorium"


def solve_task_h30(state):
    """Create Strategy Session booking page and deactivate Chat with Alex."""
    bp_id = state.get("_nextBookingPageId", 10)
    state["bookingPages"].append({
        "id": f"bp_{bp_id}",
        "title": "Strategy Session",
        "duration": 90,
        "location": "Zoom",
        "description": "",
        "availability": {
            "days": ["Mon", "Tue", "Wed", "Thu"],
            "startTime": "13:00",
            "endTime": "17:00",
        },
        "link": "https://cal.superhuman.com/alex.morgan/strategy-session",
        "isActive": True,
    })
    state["_nextBookingPageId"] = bp_id + 1
    for bp in state["bookingPages"]:
        if bp["title"] == "Chat with Alex":
            bp["isActive"] = False


def solve_task_h31(state):
    """Star the infrastructure migration email with thread (id=4)."""
    for e in state["emails"]:
        if e["id"] == 4:
            e["isStarred"] = True
            break


def solve_task_h32(state):
    """Unsubscribe from all newsletter senders in Other split."""
    newsletter_senders = [
        "newsletter@theinformation.com",
        "newsletter@techcrunch.com",
        "hello@producthunt.com",
        "crew@morningbrew.com",
        "digest@hackernewsletter.com",
    ]
    if "blockedSenders" not in state["settings"]:
        state["settings"]["blockedSenders"] = []
    for sender in newsletter_senders:
        if sender not in state["settings"]["blockedSenders"]:
            state["settings"]["blockedSenders"].append(sender)
    for e in state["emails"]:
        if e["from"]["email"] in newsletter_senders:
            e["isDone"] = True
            e["isRead"] = True


def solve_task_h33(state):
    """Create 'Follow-up Needed' label (orange) and apply to reminder emails."""
    next_id = state.get("_nextLabelId", 30)
    label_id = f"label_{next_id}"
    state["labels"].append({
        "id": label_id,
        "name": "Follow-up Needed",
        "type": "user",
        "color": "#FF9800",
    })
    state["_nextLabelId"] = next_id + 1
    reminder_ids = {64, 65, 66, 67, 111, 112}
    for e in state["emails"]:
        if e["id"] in reminder_ids:
            if label_id not in e["labels"]:
                e["labels"].append(label_id)


def solve_task_h34(state):
    """Delete snippets with open rate below 80%."""
    # snip_4 (0.76), snip_9 (0.71), snip_11 (0.68)
    to_delete = {"[Sales] Product Demo", "[Engineering] Bug Report Response",
                 "[Marketing] Event Invitation"}
    state["snippets"] = [s for s in state["snippets"]
                         if s["name"] not in to_delete]


def solve_task_h35(state):
    """Dark mode, Pacific timezone, Tokyo secondary."""
    state["settings"]["theme"] = "dark"
    state["settings"]["timezone"] = "America/Los_Angeles"
    state["settings"]["secondaryTimezone"] = "Asia/Tokyo"


def solve_task_h36(state):
    """Move email with teammate draft to inbox and add Work label."""
    for e in state["emails"]:
        if e.get("replyDraftingTeammate"):
            e["isDone"] = False
            if "label_1" not in e["labels"]:
                e["labels"].append("label_1")
            break


def solve_task_h37(state):
    """Reply to CloudScale contract email."""
    next_id = state.get("_nextEmailId", 200)
    state["emails"].insert(0, {
        "id": next_id,
        "threadId": f"thread_{next_id + 1}",
        "from": {"name": state["currentUser"]["name"],
                 "email": state["currentUser"]["email"]},
        "to": [{"name": "Michael Foster", "email": "michael.f@cloudscale.dev"}],
        "cc": [], "bcc": [],
        "subject": "Re: CloudScale Contract - Ready to Sign",
        "snippet": "Michael, confirming we'll proceed with signing the agreement.",
        "body": "Hi Michael,\n\nThanks for finalizing the contract. Confirming we'll proceed with signing the agreement.\n\nBest,\nAlex",
        "date": "2026-03-07T12:00:00.000Z",
        "isRead": True, "isStarred": False, "isDone": False, "isTrashed": False,
        "isSpam": False, "isDraft": False, "labels": [],
        "hasAttachments": False, "attachments": [],
        "splitCategory": "important", "remindAt": None,
        "readReceipt": {"opened": False}, "autoLabel": None,
        "replyDraftingTeammate": None, "threadMessages": None,
    })
    state["_nextEmailId"] = next_id + 1


def solve_task_h38(state):
    """Create 'Awaiting Reply' label (yellow) and apply to sent reminder emails."""
    next_id = state.get("_nextLabelId", 30)
    label_id = f"label_{next_id}"
    state["labels"].append({
        "id": label_id,
        "name": "Awaiting Reply",
        "type": "user",
        "color": "#FFC107",
    })
    state["_nextLabelId"] = next_id + 1
    sent_reminder_ids = {111, 112}
    for e in state["emails"]:
        if e["id"] in sent_reminder_ids:
            if label_id not in e["labels"]:
                e["labels"].append(label_id)


def solve_task_h39(state):
    """Delete personal calendar events and remove secondary timezone."""
    state["calendarEvents"] = [e for e in state["calendarEvents"]
                                if e.get("calendarId") != "personal"]
    state["settings"]["secondaryTimezone"] = ""


def solve_task_h40(state):
    """Auto-reminders external, disable auto drafts, enable Shipping Update."""
    state["settings"]["autoReminders"]["mode"] = "external"
    state["settings"]["autoDrafts"]["enabled"] = False
    al = find_auto_label(state, "Shipping Update")
    al["enabled"] = True


SOLVERS = {}
for _diff in ("e", "m", "h"):
    for _i in range(1, 41):
        _key = f"task_{_diff}{_i}"
        _fn = f"solve_task_{_diff}{_i}"
        if _fn in globals():
            SOLVERS[_key] = globals()[_fn]


# -- server management -------------------------------------------------------

def generate_seed_state():
    data_js = str(APP_DIR / "js" / "data.js")
    result = subprocess.run(
        ["node", "-e", _SEED_STATE_JS, data_js],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate seed state:\n{result.stderr}")
    return json.loads(result.stdout)


def seed_server(server_url, seed_state):
    resp = requests.put(
        f"{server_url}/api/state",
        json=seed_state,
        headers={"Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to seed server: HTTP {resp.status_code}")


def find_free_port(start=9500):
    port = start
    while port < start + 200:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(f"No free port found in range {start}-{start+200}")


def start_server(port):
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            requests.get(f"http://localhost:{port}/", timeout=1)
            return proc
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.2)
    proc.kill()
    raise RuntimeError(f"Server failed to start on port {port}")


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# -- task runner --------------------------------------------------------------

def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def load_verifier(verify_path):
    full_path = APP_DIR / verify_path
    spec = importlib.util.spec_from_file_location("verifier", str(full_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify


def run_single_task(task, server_url):
    task_id = task["id"]
    solver = SOLVERS.get(task_id)
    if not solver:
        return task_id, False, f"No solver defined for {task_id}"

    try:
        # 1. Reset to seed state
        resp = requests.post(f"{server_url}/api/reset")
        if resp.status_code != 200:
            return task_id, False, f"Reset failed: HTTP {resp.status_code}"

        time.sleep(0.3)

        # 2. Read seed state
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return task_id, False, f"Could not read state after reset: HTTP {resp.status_code}"
        state = resp.json()

        # 3. Apply the solve function
        solver(state)

        # 4. Write solved state back
        resp = requests.put(
            f"{server_url}/api/state",
            json=state,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return task_id, False, f"Could not write state: HTTP {resp.status_code}"

        # 5. Run the verifier
        verify_fn = load_verifier(task["verify"])
        passed, message = verify_fn(server_url)
        return task_id, passed, message

    except Exception as e:
        return task_id, False, f"Exception: {e}"


def run_tasks_sequential(tasks, port, seed_state):
    proc = start_server(port)
    server_url = f"http://localhost:{port}"
    results = []
    try:
        seed_server(server_url, seed_state)
        for task in tasks:
            result = run_single_task(task, server_url)
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")
    finally:
        stop_server(proc)
    return results


def run_tasks_parallel(tasks, workers, base_port, seed_state):
    results = []

    def worker_fn(task, port):
        proc = start_server(port)
        server_url = f"http://localhost:{port}"
        try:
            seed_server(server_url, seed_state)
            return run_single_task(task, server_url)
        finally:
            stop_server(proc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for i, task in enumerate(tasks):
            port = base_port + i
            future = executor.submit(worker_fn, task, port)
            futures[future] = task["id"]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "\033[32m  PASS\033[0m" if result[1] else "\033[31m  FAIL\033[0m"
            print(f"{status}  {result[0]:12s}  {result[2]}")

    return results


# -- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Superhuman Mail real-task sanity check")
    parser.add_argument("--task-id", type=str, help="Run a single task by ID")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--port", type=int, default=9500, help="Base port for servers")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.task_id:
        tasks = [t for t in tasks if t["id"] == args.task_id]
        if not tasks:
            print(f"Task '{args.task_id}' not found.")
            sys.exit(1)

    print("Generating seed state from JS data...")
    seed_state = generate_seed_state()
    print(f"Running {len(tasks)} task(s)...\n")

    if args.workers <= 1:
        port = find_free_port(args.port)
        results = run_tasks_sequential(tasks, port, seed_state)
    else:
        results = run_tasks_parallel(tasks, args.workers, args.port, seed_state)

    # Summary
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    failed = [tid for tid, p, _ in results if not p]

    print(f"\n{passed}/{total} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
