---
name: eod-shutdown
description: "Run the EightX End-of-Day Shutdown process — a Ritz-Carlton-grade daily closing ritual that reviews all communications, meetings, and deliverables, then closes open loops with clients, team members, and partners. Triggers on any request involving 'run shutdown', 'end of day', 'EOD shutdown', 'daily close', 'close out the day', 'wrap up the day', or 'shutdown process'. This skill gathers data from Gmail, Slack, Fireflies, Google Calendar, and Google Drive, analyzes open loops, sends internal follow-ups automatically, drafts client-facing messages for approval, updates the deliverables tracker, and prepares tomorrow's briefing."
---

# EightX End-of-Day Shutdown

## Overview

This is the EightX daily shutdown process — the operational engine behind our commitment to being the Ritz-Carlton of fractional CFO firms.

The Ritz-Carlton doesn't just respond to guest requests. They anticipate needs before they're expressed. They remember every preference. They make every interaction feel like you're the only guest that matters. That's the standard.

**What this means for every shutdown:**
- We don't just answer emails — we answer them in a way that makes the client feel heard, understood, and taken care of. Every draft reply should leave the client more confident in us than before they read it.
- We don't just track deliverables — we proactively update clients before they have to ask. If something is late, we tell them first, with a plan. If something is ahead of schedule, we tell them that too.
- We don't just attend meetings — we follow up with recaps that prove we were listening, that we understood what matters to them, and that we're already acting on it.
- We remember everything. Client Memory files capture preferences, frustrations, wins, and personal details so that every future interaction is informed by our history together. A client should never have to repeat themselves.
- We look for moments to add unexpected value. A relevant article. A congratulations on a milestone. A heads-up about a risk they haven't seen yet. These touches compound into trust.

The shutdown runs in phases: **Gather → Analyze → Close Loops → Update Tracker → Update Client Memory → Tomorrow Prep**. It takes 30-60 minutes depending on the volume of the day. The operator reviews and approves external Slack messages before they're sent. Client emails are placed directly into Gmail drafts for the user to review and send.

## When to Use

- User says "run shutdown," "EOD shutdown," "end of day," "close out the day," "daily close," "wrap up," or similar
- User triggers this at their preferred end-of-day time
- Can be run by Matt or any of the 5 CFOs on the team

## MCP Tool Reference

All tool calls in this skill use these MCP servers. Every tool name below is the exact callable name.

| Server | Prefix | Purpose |
|--------|--------|---------|
| Gmail/Workspace | `mcp__claude_ai_gmail-mcp__` | Gmail, Drive, Docs, Sheets (basic), Slides |
| Google Sheets | `mcp__claude_ai_gsheets-mcp__` | Advanced spreadsheet ops (read/write/format) |
| Slack | `mcp__claude_ai_Slack__` | Slack search, send, read |
| Fireflies | `mcp__claude_ai_fireflies-mcp__` | Meeting transcripts, summaries, action items |

**Not connected:** Google Calendar (no MCP). Use Fireflies + Gmail calendar notifications as workaround.

## Brand Voice for All External Communications

All client-facing messages must follow EightX brand voice:

**Tone**: Authoritative, empathetic, and forward-thinking.
**Voice**: Confident but not overbearing, reassuring but not patronizing, practical but still inspiring.
**Language**: Simple, approachable, and free from jargon, while still reflecting deep expertise.

**Style rules for shutdown communications:**
1. Lead with value or action — never "just checking in" or "circling back"
2. Short, impactful sentences mixed with longer explanations when needed
3. Every client touchpoint should leave them feeling *more* confident in EightX
4. Be specific — "We reviewed your Q1 inventory turns and have a recommendation" not "We looked at some numbers"
5. Use the founder/CEO's name, never "Dear Client"
6. Sign off warmly but professionally — the CFO's name, not "The EightX Team"
7. No jargon. Write "you're spending $95 to acquire a customer who spends $160" not "your CAC:AOV ratio is favorable"
8. When delivering a recap, frame problems as "here's what we found and here's the plan" — never just flag issues without direction

## Phase 1: Gather (Automated)

Run all of these data-gathering steps. Use parallel tool calls where possible to save time.

### 1A. Get Current Time and User Context
```
- The current date and timezone are available from your system context (no tool call needed).
- Use this to define "today" boundaries in the user's timezone:
  today_start = start of today at 00:00:00 in user's timezone
  today_end = end of today at 23:59:59 in user's timezone
  tomorrow_date = tomorrow's date (for exclusive upper bounds)
- Convert to UTC/RFC3339/Unix timestamps as needed for each API

DATE FILTERING RULES (critical — get this wrong and you miss the whole day):
- Gmail "after:" is EXCLUSIVE (after:2026/02/12 means AFTER Feb 12, missing all of Feb 12)
  → Use after:{yesterday_date} before:{tomorrow_date} to capture all of today
  → Example for Feb 12: after:2026/02/11 before:2026/02/13
- Gmail "newer_than:" is inclusive and relative — prefer this when possible
- Fireflies from_date/to_date are DATE strings (YYYY-MM-DD) and inclusive
  → Use from_date = today's date, to_date = today's date (same day = that whole day)
- Google Drive modifiedTime uses comparison operators
  → Use modifiedTime >= '{today_start_iso}' (greater than or equal)
- Slack on: filter captures the full day, after:/before: are exclusive
  → Prefer on:{today_date}, or use after:{yesterday_date} before:{tomorrow_date}
```

### 1B. Today's Calendar
```
⚠️ NO GOOGLE CALENDAR MCP IS CONNECTED. Work around this:

OPTION A (preferred): Ask the user to paste or describe today's calendar.

OPTION B: Reconstruct from other sources (run in parallel):

  1. Search Gmail for calendar notifications:
     Call mcp__claude_ai_gmail-mcp__search_gmail_messages
       query: "newer_than:1d (invite.ics OR calendar-notification OR 'accepted this invitation')"

  2. Pull today's Fireflies transcripts (auto-recorded from calendar events):
     Call mcp__claude_ai_fireflies-mcp__list_transcripts
       from_date: "{today_date}", to_date: "{today_date}"
     This shows which meetings actually happened, with attendees and times.

- Capture: meeting titles, attendees, times, descriptions
- This is the backbone — meetings drive most action items
```

### 1C. Gmail — ALL Unanswered, ALL Unread, and Sent
```
CRITICAL: Do NOT stop at the first page of results. Gmail returns paginated results
with a nextPageToken. You MUST paginate through ALL pages until there are no more results.

STEP 1 — Get ALL unread emails (paginate fully):
- Call mcp__claude_ai_gmail-mcp__search_gmail_messages
    query: "is:unread is:inbox"
- If the response includes a nextPageToken, call again with page_token = that token
- Repeat until no nextPageToken is returned
- This may take 3-10 calls depending on inbox volume — do them all

STEP 2 — Get ALL unanswered emails (paginate fully):
- Call mcp__claude_ai_gmail-mcp__search_gmail_messages
    query: "in:inbox -from:me newer_than:7d"
- Paginate through ALL pages (same as above)
- For each thread found, call mcp__claude_ai_gmail-mcp__get_gmail_thread_content
    thread_id: "{thread_id}"
  Check: Is the most recent message in the thread FROM someone other than the user?
  If yes → this is UNANSWERED and needs a response or triage
- Note: some emails from Step 1 will overlap with Step 2. Deduplicate by thread_id.

STEP 3 — Get today's sent emails:
- Call mcp__claude_ai_gmail-mcp__search_gmail_messages
    query: "after:{yesterday_date} before:{tomorrow_date} from:me"
- Paginate if needed

STEP 4 — Categorize EVERY email into one of these buckets:

  CLIENT — From/to someone at a known client company
  → Action: Read full thread. Draft reply in Gmail drafts if unanswered.

  TEAM — Internal EightX email
  → Action: Auto-reply or flag for user.

  PARTNER/LEAD — From vendors, referral partners, prospects, leads
  → Action: Read full thread. Draft reply in Gmail drafts if unanswered.

  NEWSLETTER — Automated content, marketing emails, industry digests,
  subscription emails, DTC Index, point.me deals, etc.
  → Action: Summarize key takeaways in a single digest for the user.
  Do NOT draft replies to newsletters.
  To check for a "Newsletter" label:
    Call mcp__claude_ai_gmail-mcp__list_gmail_labels
  At minimum, clearly separate newsletters from actionable emails in the briefing.

  NOTIFICATION/AUTOMATED — Payroll confirmations (QuickBooks, Gusto),
  verification codes, receipts, system notifications
  → Action: Briefly note in FYI summary. No response needed.
  Do not clutter the briefing with these — one line each at most.

  LOW PRIORITY — Everything else that doesn't fit above
  → Action: Note in FYI summary if relevant, skip if not.

STEP 5 — For ALL emails categorized as CLIENT, PARTNER/LEAD, or TEAM
that are UNANSWERED:
- Call mcp__claude_ai_gmail-mcp__get_gmail_thread_content
    thread_id: "{thread_id}"
  to get the FULL conversation history
- If the thread references other conversations, search for and read those too
- These are the emails that will get draft replies in Phase 3

The goal: ZERO unanswered client or partner emails by end of shutdown.
Every single one either gets a draft reply or gets explicitly triaged
with the user ("This one can wait because X — agree?").
```

### 1D. Slack — Messages and Threads
```
- Search public channels for messages mentioning the user today:
  Call mcp__claude_ai_Slack__slack_search_public
    query: "on:{today_date}"
    (e.g., "on:2026-02-12" — the on: filter captures the full day)

- Search DMs and private channels:
  Call mcp__claude_ai_Slack__slack_search_public_and_private
    query: "on:{today_date}"

- For threads that need context, read the full thread:
  Call mcp__claude_ai_Slack__slack_read_thread
    channel_id: "{channel_id}", thread_ts: "{thread_ts}"

- To understand a channel's recent context:
  Call mcp__claude_ai_Slack__slack_read_channel
    channel_id: "{channel_id}"

- Check for any unresolved threads where the user was mentioned but hasn't replied

- Categorize:
  - CLIENT-RELATED (client channels, client discussions)
  - TEAM (internal coordination, questions)
  - ACTION REQUIRED (someone asked a question or made a request)
  - FYI ONLY (announcements, updates)
```

### 1E. Fireflies — Today's Meeting Transcripts
```
- Get today's transcripts:
  Call mcp__claude_ai_fireflies-mcp__list_transcripts
    from_date: "{today_date}", to_date: "{today_date}"

- For each transcript found, get the AI summary:
  Call mcp__claude_ai_fireflies-mcp__get_transcript_summary
    transcript_id: "{transcript_id}"
  Returns: overview, action items, key topics, keywords, outline, chapters

- Extract action items specifically:
  Call mcp__claude_ai_fireflies-mcp__get_action_items
    transcript_id: "{transcript_id}"

- If a meeting seems particularly important (client call, strategy session),
  get the full transcript:
  Call mcp__claude_ai_fireflies-mcp__get_transcript
    transcript_id: "{transcript_id}"

- To understand meeting dynamics and engagement:
  Call mcp__claude_ai_fireflies-mcp__get_transcript_analytics
    transcript_id: "{transcript_id}"

- To get attendee details (names, emails):
  Call mcp__claude_ai_fireflies-mcp__get_meeting_attendees
    transcript_id: "{transcript_id}"
```

### 1F. Google Drive — Files Created/Modified Today
```
- Search for files modified today:
  Call mcp__claude_ai_gmail-mcp__search_drive_files
    query: "modifiedTime >= '{today_start_iso}'"
    (e.g., "modifiedTime >= '2026-02-12T00:00:00'" — note >= not > for inclusive)

- Note any deliverables that were worked on today
- Note any new files shared with the user
```

### 1G. Deliverables Tracker — Previous State
```
- The EightX Deliverables Tracker lives at a fixed location:
  Spreadsheet ID: 1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g
  URL: https://docs.google.com/spreadsheets/d/1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g/

- Read its current state:
  Call mcp__claude_ai_gsheets-mcp__read_range
    spreadsheet_id: "1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g"
    range: "Sheet1"

- Do NOT search for it — go directly to this ID every time
```

### 1H. Client Memory Files
```
- All Client Memory files live in a single shared folder:
  Folder ID: 1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw
  URL: https://drive.google.com/drive/folders/1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw

- Based on today's calendar, emails, and Slack, identify which clients were touched today

- List all files in the Client Memory folder:
  Call mcp__claude_ai_gmail-mcp__list_drive_items
    folder_id: "1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw"

- For each client touched today, look for "_CLIENT_MEMORY - [Client Name].md"
  (e.g., "_CLIENT_MEMORY - HAVN.md", "_CLIENT_MEMORY - CouchHaus.md")

- If found, read the file:
  Call mcp__claude_ai_gmail-mcp__get_doc_content
    document_id: "{file_id}"

- If not found for a client touched today, note that a new file needs to be
  created in Phase 4B (in folder_id: 1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw)

- Store the contents — you'll use them throughout the shutdown to personalize everything
```

## Phase 2: Analyze

After gathering all data, synthesize it into an actionable picture. Present this to the user as a structured briefing.

### 2A. Open Loops Identification

Cross-reference all data sources to find open loops:

**Client Open Loops** (HIGHEST PRIORITY)
- Emails from clients that are UNANSWERED (last message in thread is not from us — regardless of read status)
- Action items from today's client meetings (from Fireflies)
- Commitments made in meetings that need follow-up emails
- Deliverables that were discussed but not yet delivered
- Any client who hasn't heard from us in >48 hours (check recent sent mail)

**Team Open Loops**
- Slack messages from team members awaiting response
- Internal emails needing replies
- Action items assigned to the user from team meetings
- Handoff items between CFOs

**Partner/External Open Loops**
- Vendor emails needing response
- Referral partner follow-ups
- Lead/prospect communications

### 2B. Meeting Recap Needs

For each client meeting today, determine if a recap email is needed:
- **Always send a recap** if: new action items were identified, decisions were made, or deliverables were discussed
- **Skip recap** if: it was a brief internal sync with no client-facing implications
- Draft recaps should include: summary of what was discussed, decisions made, action items with owners, next meeting date if scheduled

### 2C. Ritz-Carlton Touch Opportunities

Identify proactive touchpoints that go beyond "responding to what came in":
- Client who had a big win today (hit a revenue milestone, closed a deal) → congratulations note
- Client who mentioned a concern in a meeting → proactive "we're on it" follow-up
- Client approaching a deliverable deadline → status update even if they didn't ask
- Any client where the last touchpoint was >5 business days ago → check-in

### 2D. Present the Briefing

Display a structured summary to the user:

```
## 🔴 MUST CLOSE TODAY (Client-Facing)
1. [Client Name] — [What needs to happen] — [Source: email/meeting/slack]
2. ...

## 🟡 SHOULD CLOSE TODAY (Team/Internal)
1. [Person] — [What needs to happen] — [Source]
2. ...

## 🟢 RITZ-CARLTON TOUCHES (Proactive)
1. [Client Name] — [Suggested touchpoint] — [Why]
2. ...

## 📋 MEETING RECAPS NEEDED
1. [Meeting title] with [Client] — [Key items to include]
2. ...

## 📧 EMAIL STATUS — Full Accounting
Unread: X total
Unanswered (need reply): X total
  - Client: X emails [list each]
  - Partner/Lead: X emails [list each]
  - Team: X emails [list each]
Already answered today: X
Newsletters: X (see digest below)
Notifications/Automated: X (no action needed)

## 📰 NEWSLETTER DIGEST
For each newsletter received today, provide a 2-3 sentence summary
of the key takeaway. Group by topic if multiple newsletters cover
similar themes.
1. [Newsletter Name] — [Key takeaway summary]
2. ...

## ℹ️ FYI — Today's Activity Summary
- X emails received, Y replied, Z drafts created, W newsletters filed
- X Slack messages, Y threads resolved, Z pending
- X meetings attended
- X Drive files created/modified
```

## Phase 3: Close Loops

Work through each category. The key rule: **internal messages send automatically, client-facing messages are drafted for approval.**

### 3A. Auto-Send: Internal and Non-External Slack Messages

For team/internal communications, compose and send directly:

**Slack messages to NON-EXTERNAL channels** (auto-send):
```
Call mcp__claude_ai_Slack__slack_send_message
  channel_id: "{channel_id}"
  message: "{message_text}"
```
- Any channel that is NOT prefixed with `external_` or does not contain external client members
- This includes internal client channels (e.g., #client_couchhaus, #client_vush, #client_threadbeast) — these are internal EightX channels ABOUT clients, not shared with them
- Team channels (#hasan-accounting, #sales_notifications, etc.)
- DMs to EightX team members
- Reply to unanswered team questions
- Post status updates, delegate tasks, acknowledge requests with timelines
- These messages go out every day without approval

**Slack messages to EXTERNAL channels** (draft for approval):
```
Call mcp__claude_ai_Slack__slack_send_message_draft
  channel_id: "{channel_id}"
  message: "{message_text}"
```
- Any channel prefixed with `external_` (e.g., #external_threadbeast) where the client or outside parties are members
- These are treated like client-facing emails — draft and present for review
- The client can see these messages, so they must follow EightX brand voice

**How to determine channel type:**
- Channel name starts with `external_` → DRAFT FOR APPROVAL (use slack_send_message_draft)
- Channel name starts with `client_` → AUTO-SEND (internal channel about that client)
- All other channels → AUTO-SEND (unless you know external parties are present)
- To look up channel info: Call mcp__claude_ai_Slack__slack_search_channels
- When in doubt, ask the user

**Internal emails** (compose and send):
- Reply to team emails
- Forward relevant information
- Delegate tasks with clear deadlines

Style for internal/non-external messages:
- Direct and concise
- Clear on what's needed and by when
- Friendly but efficient

### 3B. Draft Client Emails Directly to Gmail

For every client-facing email, draft it directly into the user's Gmail drafts. The user will review, edit if needed, and send from their inbox. Do NOT wait for approval — just create the drafts.

**Before drafting ANY reply:**
```
- Read the FULL thread:
  Call mcp__claude_ai_gmail-mcp__get_gmail_thread_content
    thread_id: "{thread_id}"
  (Never draft from snippets)
- If the thread references prior conversations, search for and read those too:
  Call mcp__claude_ai_gmail-mcp__search_gmail_messages
    query: "{related search terms}"
- Check Client Memory for tone preferences, hot buttons, and relationship context
- Have complete context before writing a single word
```

**Meeting Recap Emails:**
```
Call mcp__claude_ai_gmail-mcp__draft_gmail_message
  subject: "{recap subject}"
  body: "{recap content}"
  body_format: "html"
  to: "{client attendee emails}"
  thread_id: "{thread_id if replying to existing thread}"
  in_reply_to: "{message_id if replying}"
  references: "{references if replying}"

Structure:
- Warm opening referencing the meeting ("Great discussion today on [topic]")
- 2-3 sentence summary of what was covered
- Action items as a clean list with owners and dates
- Next steps / next meeting
- Warm close

Set the "to" field to all client attendees from the meeting.
Use the correct thread_id/in_reply_to if this is a reply to an existing thread.
```

**Response Emails to Unanswered Threads:**
```
Call mcp__claude_ai_gmail-mcp__draft_gmail_message
  subject: "{reply subject}"
  body: "{reply content}"
  body_format: "html"
  to: "{recipient}"
  thread_id: "{thread_id}"
  in_reply_to: "{last_message_id}"
  references: "{references}"

- Read the FULL thread first — every message, not just the latest
- If the thread references other topics, search Gmail for related threads
  and read those too so the reply has complete context
- Address the client's question/concern directly
- Provide the answer or a clear timeline for when you'll have it
- Add one proactive insight if possible ("While I was looking into this, I also noticed...")

CRITICAL: Set thread_id, in_reply_to, and references fields correctly
so the draft appears as a reply in the existing thread, not a new email.
```

**Proactive Ritz-Carlton Touches:**
```
Call mcp__claude_ai_gmail-mcp__draft_gmail_message
  subject: "{proactive subject}"
  body: "{proactive content}"
  body_format: "html"
  to: "{client email}"

- Keep these brief and genuine
- Reference something specific (not generic "checking in")
- Offer value: an insight, a resource, a heads-up
- Use Client Memory to personalize — reference things they've mentioned,
  acknowledge their situation, match their preferred communication style
- Examples:
  "I was reviewing your January numbers and noticed DTC revenue jumped 18%
  week-over-week — wanted to flag that your current inventory levels may need
  adjustment if this trend holds. Let's discuss on our next call."

  "Great call today. I want to make sure [specific deliverable] is exactly
  what you need — I'll have a draft over by [specific day]. In the meantime,
  the cash flow model we discussed is already updated in your Drive folder."
```

**After creating all drafts, present a summary to the user:**
```
📧 DRAFTS CREATED IN GMAIL

1. [Client Name] — [Subject] — Reply to [person's name]'s email about [topic]
2. [Client Name] — [Subject] — Meeting recap from today's call
3. [Client Name] — [Subject] — Proactive outreach re: [topic]

These are in your Gmail drafts. Review, edit, and send at your convenience.
```

### 3C. External Slack — Draft for Approval

For messages to external Slack channels (prefixed with `external_`):
```
- Draft the message:
  Call mcp__claude_ai_Slack__slack_send_message_draft
    channel_id: "{channel_id}"
    message: "{message_text}"

- Present the draft to the user for review
- Wait for user approval before sending

- After approval, send:
  Call mcp__claude_ai_Slack__slack_send_message
    channel_id: "{channel_id}"
    message: "{approved_message_text}"

- These are the ONLY messages that require explicit approval before sending
```

## Phase 4: Deliverables Tracker Update

### Tracker Structure

The tracker is a Google Sheet called "EightX Deliverables Tracker" with these columns:

| Column | Description |
|--------|-------------|
| Client | Client company name |
| Deliverable | Description of the deliverable |
| Owner | CFO or team member responsible |
| Status | Not Started / In Progress / Under Review / Delivered / Blocked |
| Due Date | When it's due |
| Priority | High / Medium / Low |
| Last Updated | Date of last status change |
| Source | Where this was identified (meeting date, email, etc.) |
| Notes | Context, blockers, dependencies |

### First Run: Create the Tracker

The tracker already exists at spreadsheet ID: 1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g
If additional sheets or structure are needed, add them directly to this spreadsheet.
Do NOT create a new spreadsheet.

### Daily Update Process

1. **Review yesterday's tracker state** (loaded in Phase 1G)
2. **Identify new deliverables** from today's meetings, emails, and Slack
3. **Update statuses** based on today's activity:
   - Files created/modified in Drive → may indicate progress on a deliverable
   - Emails sent with attachments → may indicate delivery
   - Meeting discussions about deliverable status → update notes
4. **Flag overdue items** — anything past its due date
5. **Flag items with no activity in 5+ days** — these may be stuck
6. **Present changes to user** before saving:
   ```
   📋 DELIVERABLES TRACKER UPDATE

   NEW (added today):
   - [Client] — [Deliverable] — Due [date] — Owner: [name]

   UPDATED:
   - [Client] — [Deliverable] — Status changed to [new status]

   ⚠️ OVERDUE:
   - [Client] — [Deliverable] — Was due [date] — [X days overdue]

   ⚠️ STALE (no activity in 5+ days):
   - [Client] — [Deliverable] — Last updated [date]
   ```

7. **Write updates to the tracker:**
```
- To update existing rows:
  Call mcp__claude_ai_gsheets-mcp__write_range
    spreadsheet_id: "1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g"
    range: "{specific range, e.g., Sheet1!A5:I5}"
    values: [[...row data...]]

- To add new deliverables:
  Call mcp__claude_ai_gsheets-mcp__append_rows
    spreadsheet_id: "1Seq9RuMoNxYgo0pNOmbEAK5SK2kye6vf2dcwxr2ux_g"
    range: "Sheet1"
    values: [[...new row data...]]
```

## Phase 4B: Client Memory Update

### What This Is

Every client has a living Google Doc called `_CLIENT_MEMORY.md` stored in their client folder. This is NOT a task tracker — the Deliverables Tracker handles tasks. This is a **relationship intelligence file** — the things a Ritz-Carlton concierge would write down about a guest so every future interaction feels personal, informed, and anticipatory.

This file gets appended to during every daily shutdown and referenced during every future shutdown. Over weeks and months, it becomes the most valuable document EightX has on each client — a running record of who these people are, what they care about, and how to serve them better.

### File Location and Naming

- **File name**: `_CLIENT_MEMORY.md` (underscore prefix keeps it sorted to top of folder)
- **Location**: Inside the Client Memory Google Drive folder
- **Format**: Google Doc (created via import_to_google_doc with markdown content)

### Finding or Creating the File

During Phase 1 (Gather), for every client touched today:

```
1. List files in the Client Memory folder:
   Call mcp__claude_ai_gmail-mcp__list_drive_items
     folder_id: "1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw"

2. Look for "_CLIENT_MEMORY - [Client Name].md" in the listing

3. If found: Read current contents so you can reference prior entries:
   Call mcp__claude_ai_gmail-mcp__get_doc_content
     document_id: "{file_id}"

4. If NOT found: Create the file during Phase 4B:
   Call mcp__claude_ai_gmail-mcp__import_to_google_doc
     file_name: "_CLIENT_MEMORY - [Client Name]"
     content: "{initial template markdown}"
     folder_id: "1UvBhHNiJjnPWs6mc1zMXaBFpGrtUYcWw"
   Populate with the initial template below.
```

### File Structure

The file has two sections: a slow-changing **Profile** at the top, and a chronological **Memory Stream** that grows over time.

```markdown
# [Client Name] — Client Memory

## Profile
_Updated whenever something changes. Not every shutdown._

**Primary Contact(s):** [Name, role, email]
**Communication Style:** [How they prefer to interact — email vs Slack, level of detail they want, response time expectations]
**Decision-Making:** [Do they want options or recommendations? Do they decide fast or need time? Do they loop in others?]
**Hot Buttons:** [Topics that make them anxious, things previous providers got wrong, pet peeves]
**What They Value Most:** [Speed? Accuracy? Hand-holding? Autonomy? Being kept in the loop?]
**Personal Notes:** [Kids, hobbies, travel plans, health mentions — things that make us human]
**Business Context:** [One paragraph narrative of where they are in their journey — updated monthly]

---

## Memory Stream
_Newest entries at the top. One entry per shutdown that touched this client._

### [YYYY-MM-DD] — Daily Shutdown
- **Mood/Tone:** [How did they seem today? Stressed, excited, frustrated, neutral?]
- **Key Observations:** [What happened that's worth remembering?]
- **Preferences Learned:** [Anything new about how they like to work?]
- **Issues/Friction:** [Problems that came up — with us, their business, their team]
- **Wins:** [Things that went well — celebrate these]
- **Relationship Notes:** [Anything personal mentioned, dynamics observed]
```

### What to Capture (and What NOT to Capture)

**DO capture:**
- "Arthur seemed frustrated that the inventory report wasn't formatted the way he expected. He wants tables, not bullet points."
- "Crystal mentioned she's going to China in March for supplier meetings. Good opportunity for us to prep a negotiation framework."
- "Harrison said he's overwhelmed managing two stores. He appreciated when we proactively flagged the cash dip — he wants us to always lead with risks, not bury them."
- "Uday prefers Slack over email for quick updates. Only use email for formal deliverables."
- "Stephanie mentioned she's struggling with the insurance process. She sounded stressed — follow up with a reassuring note, not just task updates."
- "The team dynamic between Danny and Ben seems tense. Crystal is caught in the middle. Be careful how we position cost-cutting recommendations."
- "Mike (advisor) carries significant influence. When Mike speaks, Crystal listens. Route important strategic recommendations through contexts where Mike is present."

**DO NOT capture:**
- Specific dollar amounts or financial metrics (those live in the financial model)
- Individual task statuses (those live in the Deliverables Tracker)
- Meeting minutes or action items (those live in Fireflies and recap emails)
- Anything that's already in another system — this file is for the stuff that lives nowhere else

### Daily Update Process

After Phase 3 (Close Loops) and Phase 4 (Deliverables Tracker), for each client that was touched today:

```
1. Review today's signals for this client:
   - Fireflies transcript summaries and action items
   - Emails sent/received
   - Slack messages in client channels
   - Any meetings attended

2. Ask: "What did we learn about this person/team TODAY that we'd
   want to remember NEXT TIME we interact with them?"

3. Write a concise Memory Stream entry. Keep it to 3-6 bullet points.
   Focus on the human/relational signal, not the task details.

4. Check if any Profile fields need updating:
   - New contact added to the relationship?
   - Communication preference revealed?
   - Decision-making pattern observed?
   - New personal detail mentioned?

5. Update the Google Doc:
   - Read current state:
     Call mcp__claude_ai_gmail-mcp__get_doc_content
       document_id: "{file_id}"
   - Prepend the new entry to the Memory Stream section (newest first):
     Call mcp__claude_ai_gmail-mcp__modify_doc_text
       document_id: "{file_id}"
       start_index: {index after "## Memory Stream" header}
       text: "{new entry text}"
   - For more complex updates (Profile + Memory Stream in one pass):
     Call mcp__claude_ai_gmail-mcp__batch_update_doc
       document_id: "{file_id}"
       operations: [{...insert/replace operations...}]

6. Present the entry to the user for review:
   "📝 CLIENT MEMORY UPDATE — [Client Name]
   [Show the entry]
   Anything to add or change before I save this?"
```

### Weekly Enhancement (Fridays)

On Friday shutdowns, in addition to the daily entry, also:

```
1. Review the week's Memory Stream entries for each active client
2. Synthesize a "Weekly Pattern" observation if one exists:
   - "This week's theme for [Client]: Cash anxiety. They asked about
     runway in two separate calls and mentioned it in Slack."
   - "Trend: Harrison is increasingly delegating financial questions
     to Paige. She may be the primary contact soon."
3. Update the Business Context paragraph in the Profile if the
   narrative has shifted
4. Flag any client where the Memory Stream reveals a pattern that
   should change our approach
```

### How the Shutdown Uses Client Memory

During Phase 2 (Analyze), when evaluating open loops and Ritz-Carlton touches:

```
- Read the _CLIENT_MEMORY.md for each client being discussed
- Use it to:
  * Tailor the tone of drafted messages (if they're stressed, lead with reassurance)
  * Reference things they've mentioned (shows we listen)
  * Avoid known hot buttons
  * Choose the right communication channel (their preference)
  * Identify when a client's pattern suggests they need proactive outreach
    even if they haven't asked for anything
  * Personalize Ritz-Carlton touches with specifics, not generic outreach
```

### Example: First Entry for a New Client

```markdown
# HAVN — Client Memory

## Profile

**Primary Contact(s):** Arthur Menard de Calenge, CEO/Founder (arthur@havnwear.com)
**Communication Style:** TBD — first week of engagement
**Decision-Making:** TBD
**Hot Buttons:** TBD
**What They Value Most:** TBD
**Personal Notes:** TBD
**Business Context:** HAVN is a fast-scaling DTC EMF protection brand. Went from $300K/mo to $1.8M/mo in 5 months. 78% gross margins. Seeking $2M inventory financing. First week of EightX engagement — kickoff held Feb 11, 2026. Team assigned: Matt (lead), Ashutosh, Gabriela, Patricia, Shin.

---

## Memory Stream

### 2026-02-11 — Daily Shutdown (Kickoff Day)
- **Mood/Tone:** Arthur was engaged and enthusiastic during kickoff. High energy, clearly proud of the growth trajectory.
- **Key Observations:** Internal call after kickoff focused on automating 13-week cash flow and revenue forecasts. Matt emphasized "Ritz-Carlton standard" for client communication with this account.
- **Preferences Learned:** Early signal — Arthur attended kickoff via Google Meet, team used internal call for strategy. Keep client-facing interactions clean and separate from internal planning.
- **Issues/Friction:** None on day one. Account setup is the priority — need to centralize data access and be careful with permissions.
- **Wins:** Kickoff completed. Full EightX senior team assigned. Strong first impression.
- **Relationship Notes:** Multiple team members assigned (5 EightX people). Important to have clear single point of contact for Arthur so he's not confused about who to go to.
```

## Phase 5: Tomorrow Prep

### 5A. Tomorrow's Calendar Preview
```
⚠️ NO GOOGLE CALENDAR MCP IS CONNECTED. Work around this:

- Ask the user about tomorrow's schedule, OR
- Search Gmail for tomorrow's calendar notifications:
  Call mcp__claude_ai_gmail-mcp__search_gmail_messages
    query: "newer_than:2d (invite.ics OR calendar-notification) {tomorrow_date}"

- List meetings with: time, client/attendees, purpose
- Flag any meetings that need prep (client reviews, strategy sessions)
- Note any gaps that could be used for deep work on deliverables
```

### 5B. Tomorrow's Priority List
```
Based on everything from today, create a prioritized list:

🔴 MUST DO TOMORROW
- [Item] — [Why it's urgent]

🟡 SHOULD DO TOMORROW
- [Item] — [Context]

🟢 IF TIME ALLOWS
- [Item] — [Context]
```

### 5C. Weekly Client Summary Check (Fridays Only)

If today is Friday, also draft a weekly summary for each active client:
```
Structure:
- What we accomplished this week
- Key metrics or findings
- What's coming next week
- Any decisions needed from the client

Deliver as: Email draft from the CFO:
  Call mcp__claude_ai_gmail-mcp__draft_gmail_message
    subject: "[Client Name] — Weekly Update from EightX"
    body: "{weekly summary content}"
    body_format: "html"
    to: "{client email}"

Optionally create a detailed summary doc:
  Call mcp__claude_ai_gmail-mcp__create_doc
    title: "[Client Name] — Week of {date} Summary"
    content: "{detailed summary}"
```

**Weekly Slack Updates (Fridays Only):**
The same daily Slack rules apply to weekly updates:
```
- Non-external channels (client_*, team channels, DMs) → auto-send:
  Call mcp__claude_ai_Slack__slack_send_message
    channel_id: "{channel_id}"
    message: "{weekly summary}"

- External channels (external_*) → draft for approval:
  Call mcp__claude_ai_Slack__slack_send_message_draft
    channel_id: "{channel_id}"
    message: "{weekly summary}"
```
- Weekly Slack updates in internal client channels should summarize the week's
  key activities, flag anything that needs attention next week, and note any
  client sentiment shifts from the Client Memory file

### 5D. Shutdown Confirmation

End with a clean summary:
```
✅ SHUTDOWN COMPLETE — [Date]

📧 Emails: X drafts created in Gmail (Y client, Z team)
💬 Slack: X messages sent (Y auto-sent internal, Z external drafted)
📋 Deliverables: X new, Y updated, Z overdue
🧠 Client Memory: X clients updated, Y new files created
📅 Tomorrow: X meetings, top priority is [item]

All open loops closed. Have a great evening.
```

## Important Notes

### Handling Sensitive Information
- Never include specific financial figures in Slack channels — use email or DM for sensitive data
- Client information should not cross between client channels
- When in doubt about sensitivity, draft for approval rather than auto-sending

### When Things Are Quiet
- If it's a light day with few open loops, the shutdown is shorter — that's fine
- Still run the Ritz-Carlton touch check — quiet days are the BEST days for proactive outreach
- Still update the deliverables tracker — consistency is the whole point

### Error Handling
- If a tool fails (Fireflies down, Slack timeout), note what couldn't be checked and move on
- If Gmail can't be searched, that's the most critical gap — flag it prominently
- The shutdown should always complete even if some data sources are unavailable

### Team Rollout
- Each CFO runs their own shutdown from their own Claude account
- Each CFO manages their own client roster — the tracker can be filtered by Owner
- Matt can run a "meta-shutdown" that reviews all CFOs' tracker updates if desired
- Consider a shared Slack channel (#daily-shutdown) where each CFO posts their completion summary

## Full Workflow Summary

```
1. User says "run shutdown" (or similar trigger)
2. GATHER: Pull data from Gmail, Slack, Fireflies, Drive, Tracker, Client Memory files
   Tools: gmail-mcp (search_gmail_messages, get_gmail_thread_content, search_drive_files,
          list_drive_items, get_doc_content), Slack (slack_search_public,
          slack_search_public_and_private, slack_read_thread), fireflies-mcp
          (list_transcripts, get_transcript_summary, get_action_items,
          get_meeting_attendees), gsheets-mcp (read_range)
3. ANALYZE: Cross-reference to find open loops, categorize by priority.
   Use Client Memory to personalize. No tool calls — pure synthesis.
4. PRESENT BRIEFING: Show structured summary to user
5. CLOSE LOOPS — INTERNAL: Auto-send team Slack messages and emails
   Tools: Slack (slack_send_message)
6. CLOSE LOOPS — CLIENT: Draft emails into Gmail drafts
   Tools: gmail-mcp (draft_gmail_message, get_gmail_thread_content)
7. CLOSE LOOPS — EXTERNAL SLACK: Draft for approval, then send
   Tools: Slack (slack_send_message_draft, slack_send_message)
8. RITZ-CARLTON TOUCHES: Draft proactive client outreach using Client Memory
   Tools: gmail-mcp (draft_gmail_message)
9. UPDATE TRACKER: Add new deliverables, update statuses, flag overdue items
   Tools: gsheets-mcp (write_range, append_rows)
10. UPDATE CLIENT MEMORY: Write memory entries for each client touched today
    Tools: gmail-mcp (get_doc_content, modify_doc_text, batch_update_doc,
           import_to_google_doc)
11. TOMORROW PREP: Preview calendar, create priority list
    Tools: gmail-mcp (search_gmail_messages), Slack (slack_send_message),
           gmail-mcp (draft_gmail_message, create_doc)
12. WEEKLY ENHANCEMENTS: (Fridays only) Client weekly recaps + Client Memory synthesis
13. CONFIRM SHUTDOWN: Display completion summary
```
