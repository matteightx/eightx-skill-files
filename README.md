# EightX Skill Files

Claude Code skills and MCP tool reference library for EightX operations.

## Structure

```
skills/                          # Claude Code skill definitions
  eod-shutdown/SKILL.md          # EOD Shutdown skill (source markdown)
  newsletter-writer/             # Newsletter Writer skill (source + references)
    SKILL.md
    references/                  # Prompt chain files + meme generator
  eod-shutdown-v2.skill          # Packaged skill (ZIP)
  newsletter-writer-v2.skill     # Packaged skill (ZIP)

tool-library/                    # Unified tool reference
  tool-library.json              # 412 tools across 6 MCP servers

sources/                         # Raw tool reference files (input for tool-library.json)
  GHL_MCP_TOOLS.txt              # 179 GoHighLevel tools
  apollo-tools-reference.txt     # 44 Apollo tools
  gmail_TOOLS.txt                # 61 Google Workspace tools
  GOOGLE SHEETS MCP.txt          # 88 Google Sheets tools
  fireflies-TOOLS.txt            # 20 Fireflies tools
  storeleads_tools.txt           # 20 StoreLeads tools
```

## Skills

### EOD Shutdown (`eod-shutdown`)
Daily closing ritual that reviews Gmail, Slack, Fireflies, and Drive to close open loops, draft client emails, update the deliverables tracker, and maintain client memory files.

### Newsletter Writer (`newsletter-writer`)
Writes Matt's weekly newsletter from advisory call transcripts using a 4-stage prompt chain (mine insight, architecture, draft, editorial polish) plus auto-generated memes.

## Tool Library

`tool-library.json` contains 412 tools in a unified schema optimized for LLM consumption. Each tool includes `name`, `source`, `category`, `description`, and `parameters`.

| Source | Tools |
|--------|-------|
| GoHighLevel (ghl) | 179 |
| Apollo (apollo) | 44 |
| Google Workspace (google_workspace) | 61 |
| Google Sheets (google_sheets) | 88 |
| Fireflies (fireflies) | 20 |
| StoreLeads (storeleads) | 20 |
