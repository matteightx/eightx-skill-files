# Meme Generation Instructions

This document describes how to create a meme image from a concept description. It is called from Stage 4 of the newsletter prompt chain after the editorial polish produces a meme concept suggestion.

## Overview

Instead of just describing a meme concept for Matt to create manually, you will:

1. **Search** for the right meme template using WebSearch
2. **Download** the template image using WebFetch
3. **Generate** the final meme using the bundled Python script
4. **Output** a ready-to-use .png file alongside the newsletter

## Step 1: Parse the Meme Concept

The editorial polish stage outputs a meme concept description like:

> "Drake meme: top panel 'Cutting ad spend to save money' / bottom panel 'Fixing your cash conversion cycle first'"

From this description, extract:
- **Template name** — the meme format (e.g., "Drake", "Distracted Boyfriend", "This Is Fine", "Expanding Brain")
- **Text content** — what goes on each text area
- **Layout type** — top/bottom text vs. multi-panel (Drake, Expanding Brain, etc.)

## Step 2: Find the Meme Template

Use the **WebSearch** tool (Claude Code built-in) to find a clean (no text) version of the meme template:

```
WebSearch query: "<template name> meme template blank"
Examples:
  - "Drake meme template blank"
  - "distracted boyfriend meme template blank"
  - "this is fine dog meme template blank"
  - "expanding brain meme template blank no text"
```

**Search strategy:**
1. First search for the specific meme template name + "blank template"
2. Look for results from imgflip.com, knowyourmeme.com, or other meme template sites
3. You need a direct image URL (ending in .jpg, .png, .webp, or from an image hosting domain)

If the concept describes a less common meme, search for it by description:
```
WebSearch query: "meme template" + key visual description
e.g., "two buttons meme template blank" or "galaxy brain meme template"
```

## Step 3: Download the Template

Use the **WebFetch** tool (Claude Code built-in) to download the template image:

```
WebFetch
  url: "<direct_image_url>"
  prompt: "Download this meme template image"
```

Save the downloaded image to disk using the **Write** tool or **Bash**:
```python
# If you received base64 image data, use Bash:
python3 -c "
import base64
with open('meme_template.png', 'wb') as f:
    f.write(base64.b64decode('{image_data}'))
"
```

**If you cannot download the image** (blocked domain, etc.), fall back to:
1. Try a different source URL from search results
2. Try another WebSearch with different query terms
3. As last resort, describe the meme concept in text (the old behavior) and note that Matt will need to create it manually

## Step 4: Generate the Meme

Install Pillow if needed (use **Bash** tool):
```bash
pip install Pillow --break-system-packages -q
```

The meme generator script is bundled in the skill references at `references/meme_generator.py`.

### For standard top/bottom memes:
```bash
python3 references/meme_generator.py \
  meme_template.png \
  newsletter_meme.png \
  --top "TOP TEXT HERE" \
  --bottom "BOTTOM TEXT HERE"
```

### For multi-panel memes (Drake, Expanding Brain, etc.):
```bash
python3 references/meme_generator.py \
  meme_template.png \
  newsletter_meme.png \
  --panels "PANEL 1 TEXT" "PANEL 2 TEXT"
```

For expanding brain (4 panels):
```bash
python3 references/meme_generator.py \
  meme_template.png \
  newsletter_meme.png \
  --panels "BASIC IDEA" "SLIGHTLY BETTER" "GETTING SMARTER" "GALAXY BRAIN MOVE"
```

### Optional: Font size override
```bash
--font-size 36
```
Use this if the auto-calculated size doesn't look right (e.g., very long text on a small template).

## Step 5: Output

1. The finished meme is at `newsletter_meme.png` in the working directory
2. Present the file to Matt (it will be visible as an image in the conversation)
3. Upload it to Google Drive alongside the newsletter doc:
   ```
   Call mcp__claude_ai_gmail-mcp__create_drive_file
     file_name: "newsletter_meme_{date}.png"
     folder_id: "{newsletter_folder_id}"
     fileUrl: "{local_file_path}"
   ```

## Common Meme Formats Reference

Quick reference for layout type so you don't have to guess:

| Meme Template | Layout | Notes |
|---|---|---|
| Drake / Drake Hotline Bling | multi-panel (2) | Text on RIGHT side of each panel |
| Distracted Boyfriend | top/bottom | Single caption or top/bottom |
| This Is Fine | top/bottom | Dog in burning room |
| Expanding Brain | multi-panel (3-5) | Text on RIGHT side |
| Two Buttons | top/bottom | Guy sweating over two buttons |
| Change My Mind | bottom only | Guy at table with sign |
| Surprised Pikachu | top/bottom | |
| Batman Slapping Robin | multi-panel (2) | Text in speech bubbles area |
| Is This a Pigeon? | top/bottom | Butterfly meme |
| Disaster Girl | top/bottom | |
| One Does Not Simply | top/bottom | Boromir |
| Stonks | top/bottom or bottom only | |
| Bernie Sanders Mittens | top/bottom | |
| Woman Yelling at Cat | multi-panel (2) | Left panel / right panel |
| Flex Tape | multi-panel (2) | |
| Always Has Been | multi-panel (2) | Astronaut meme |

## Troubleshooting

**"Template not found" error:** The download failed. Try a different URL from search results.

**Text too small/large:** Use `--font-size` to override. Good range is 24-56 depending on image size.

**Wrong layout:** If text is appearing in the wrong spot on a multi-panel meme, try switching between `--top/--bottom` and `--panels` modes.

**Can't find a blank template:** Some memes don't have clean blank versions. Search for "<meme name> meme generator" to find imgflip's version, which usually has a clean template link.

**Pillow not installed:** Run `pip install Pillow --break-system-packages` before running the script.
