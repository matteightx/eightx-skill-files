---
name: newsletter-writer
description: "Write EightX weekly newsletters from advisory call transcripts. Triggers on any request involving 'newsletter', 'write the newsletter', 'weekly email', 'newsletter from calls', 'write a newsletter from this week's calls', 'content from client calls', or when Matt asks to turn call insights into content. This skill handles the full pipeline: reviewing prior GHL campaigns to avoid duplication, scanning Fireflies call summaries to find the best insight, pulling the full transcript, running a 4-stage prompt chain (mine insight → architecture → draft → polish), generating a meme image, and outputting a formatted Google Doc. Use this skill even if the user only mentions part of the pipeline (e.g., 'find a good call for this week's newsletter')."
---

# EightX Newsletter Writer

Write Matt Putra's weekly newsletter by mining real advisory call insights and running them through a structured prompt chain that produces Hormozi/Robinson-style newsletters — complete with an auto-generated meme.

## Overview

This skill automates the full newsletter creation pipeline:

1. **Review prior campaigns** in GHL to avoid topic duplication
2. **Scan recent call summaries** from Fireflies to find the best teachable insight
3. **Pull the full transcript** of the selected call
4. **Run the 4-stage prompt chain** to produce the newsletter
5. **Generate a meme image** based on the newsletter's concept
6. **Output to Google Doc** with proper formatting

## MCP Tool Reference

All tool calls in this skill use these MCP servers. Every tool name below is the exact callable name.

| Server | Prefix | Purpose |
|--------|--------|---------|
| GHL | `mcp__claude_ai_ghl-mcp__` | Campaign history, blog posts, email templates |
| Fireflies | `mcp__claude_ai_fireflies-mcp__` | Meeting transcripts, summaries, action items, metrics |
| Gmail/Workspace | `mcp__claude_ai_gmail-mcp__` | Google Docs creation, Drive search, file management |
| Google Sheets | `mcp__claude_ai_gsheets-mcp__` | Drive search (alternate) |

**Built-in Claude Code tools** (no MCP prefix needed):
- `WebSearch` — search the web (for meme templates)
- `WebFetch` — download web content (for meme template images)
- `Bash` — run shell commands (for meme generator script, pip install)
- `Write` — write files to disk
- `Read` — read files from disk

## Step-by-Step Workflow

### Step 1: Review Prior Campaigns in GHL

Check what newsletters have already been sent to avoid repeating topics.

```
1. List all campaigns:
   Call mcp__claude_ai_ghl-mcp__campaigns_list
   (no parameters required)

2. Review recent published blog posts:
   Call mcp__claude_ai_ghl-mcp__blogs_list_posts
     status: "published"
     limit: 20

3. Check recent email templates:
   Call mcp__claude_ai_ghl-mcp__email_templates_list
     limit: 20
```

Compile a short list of recent newsletter topics/themes (last 8-12 newsletters). Present this to Matt as: "Here are your recent newsletter topics — I'll make sure we don't repeat any of these."

### Step 2: Analyze Recent Advisory Calls

Scan Fireflies transcripts from the past week to find the most newsletter-worthy insight.

```
1. Get recent transcripts (past 7 days):
   Call mcp__claude_ai_fireflies-mcp__list_transcripts
     from_date: "{7_days_ago_YYYY-MM-DD}"
     to_date: "{today_YYYY-MM-DD}"
     limit: 20

2. For each transcript, get the AI-generated summary:
   Call mcp__claude_ai_fireflies-mcp__get_transcript_summary
     transcript_id: "{transcript_id}"
   Returns: overview, action items, key topics, keywords, outline, chapters

3. Score each call against the "good newsletter topic" criteria (see below)
```

**Scoring criteria for a good newsletter topic:**
- Contains a problem the reader doesn't know they have (or underestimates)
- Has a specific, quantifiable impact (dollars, percentages, time)
- Can be distilled into a simple framework or checklist
- Positions Matt as someone who sees things others miss
- Creates urgency without fear-mongering
- Is universal — applicable to any eComm brand shipping physical products

Present the top 3 candidates to Matt with a 1-2 sentence pitch for each. Let Matt pick, or recommend the strongest one with reasoning.

### Step 3: Pull Full Transcript

Once Matt selects a call (or confirms your recommendation):

```
1. Get the full transcript with speaker attribution:
   Call mcp__claude_ai_fireflies-mcp__get_transcript
     transcript_id: "{selected_transcript_id}"

2. Extract metrics and numbers discussed:
   Call mcp__claude_ai_fireflies-mcp__get_metrics
     transcript_id: "{selected_transcript_id}"

3. Extract action items for additional context:
   Call mcp__claude_ai_fireflies-mcp__get_action_items
     transcript_id: "{selected_transcript_id}"
```

You now have the raw material for the newsletter.

### Step 4: Run the Newsletter Prompt Chain

This is a 4-stage chain. Each stage builds on the previous output. The Newsletter DNA Playbook (in `references/newsletter-dna.md`) serves as the system-level writing guidelines that inform every stage.

Before starting, read `references/newsletter-dna.md` to load the full playbook.

**Stage 1 — Mine the Insight**

Read `references/prompt-mine-insight.md` and follow its instructions using the full transcript as input. Output the mined insight document.

**Stage 2 — Build the Architecture**

Read `references/prompt-architecture.md` and follow its instructions using:
- The Newsletter DNA Playbook
- The mined insight from Stage 1

Output the architecture document with multiple options per section.

Present the architecture to Matt. Let him pick preferred options for each section (opening line, hook, framework name, PS line, sign-off). If Matt says "you pick" or wants to move fast, select the strongest options based on the DNA playbook principles.

**Stage 3 — Write the First Draft**

Read `references/prompt-first-draft.md` and follow its instructions using the selected architecture from Stage 2.

Output the full newsletter draft.

**Stage 4 — Editorial Polish**

Read `references/prompt-editorial-polish.md` and follow its instructions using the draft from Stage 3.

Output:
- The polished final newsletter
- 5 ranked subject line options
- 2-3 sentences explaining what changed and why
- A meme concept with specific template, layout, and text (see below)

### Step 5: Generate the Meme

Read `references/prompt-meme-generation.md` and follow its instructions using the meme concept from Stage 4.

This stage will:
1. **Search the web** for the specified meme template (blank/no-text version)
2. **Download** the template image
3. **Run the meme generator script** (`references/meme_generator.py`) to composite the text onto the template
4. **Output** a ready-to-use .png meme image

```
Tools used (Claude Code built-ins, not MCP):

- WebSearch: Find the blank meme template URL
  query: "{template_name} meme template blank"

- WebFetch: Download the template image
  url: "{direct_image_url}"

- Bash: Install Pillow + run the meme_generator.py script
  command: "pip install Pillow --break-system-packages -q"
  command: "python3 meme_generator.py {template_path} {output_path} --top 'TEXT' --bottom 'TEXT'"

- Write: Save downloaded image to disk if needed
```

If template download fails after multiple attempts, fall back to describing the meme concept in text and note that Matt will need to create it manually. Don't let a meme failure block the newsletter delivery.

### Step 6: Output to Google Doc

Create the final newsletter as a Google Doc:

```
1. Search for the newsletter folder in Drive:
   Call mcp__claude_ai_gmail-mcp__search_drive_files
     query: "name contains 'newsletter' and mimeType = 'application/vnd.google-apps.folder'"
   OR:
   Call mcp__claude_ai_gsheets-mcp__search_drive
     query: "newsletter"
   If no folder found, ask Matt where to save it.

2. Create the Google Doc with the final polished newsletter:
   Call mcp__claude_ai_gmail-mcp__create_doc
     title: "EightX Newsletter — {topic_name} — {date}"
     content: "{full polished newsletter text}"

   OR for richer formatting from markdown:
   Call mcp__claude_ai_gmail-mcp__import_to_google_doc
     file_name: "EightX Newsletter — {topic_name} — {date}"
     content: "{newsletter as markdown}"
     folder_id: "{newsletter_folder_id if found}"

3. If the meme was generated, upload it to Drive alongside the doc:
   Call mcp__claude_ai_gmail-mcp__create_drive_file
     file_name: "newsletter_meme_{date}.png"
     folder_id: "{newsletter_folder_id}"
     fileUrl: "{local_file_path_or_url}"
```

Format the doc with:
- Opening quote/pre-header styled distinctly (italic or different formatting)
- Clean paragraph breaks (no bullets in the body unless the framework steps warrant it)
- PS line separated with a horizontal rule
- Sign-off with Matt's name and closing phrase
- Subject line options listed at the top for easy reference

**Include the meme**: Reference the generated meme .png alongside the newsletter document.

**Alternative**: If Matt prefers a local file, output as markdown or .docx instead.

## Important Notes

- **Always anonymize** — No client names, brand identifiers, or details that could identify the client from the call
- **Word count discipline** — The newsletter body (excluding opening quote, sign-off, PS) should be 250-400 words max
- **Banned words** — Never use "game-changer," "unlock," "level up," or "deep dive"
- **Voice** — Matt speaks like a smart friend who happens to know finance. Direct, analytical, occasionally uses mild profanity for emphasis. Peer-to-peer, not consultant-to-client.
- **The litmus test** — Every newsletter must pass the "Damn, this is good even if I don't buy" standard
- **Meme quality bar** — The meme should make an eComm founder laugh or nod. If the concept feels forced or unfunny, skip it and tell Matt rather than shipping a bad meme.
