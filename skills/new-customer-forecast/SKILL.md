---
name: new-customer-forecast
description: "Populate the New_Customer_Forecast_v2 tab in the Havn Financial Model spreadsheet. Reads 24 months of funnel data (ad spend, new customers, revenue, orders, AOV, CAC), calculates base metrics and seasonal indices, writes SUMPRODUCT formulas for historicals, and sets up the forecast framework. Triggers on any request involving 'financial forecast', 'new customer forecast', 'populate the forecast', 'Havn forecast', 'revenue forecast', 'forecast tab', 'forecast model', or 'run the forecast'. This skill prescribes the exact gsheets-mcp tool calls so Claude can execute immediately without tool discovery."
---

# Financial Forecasting — Shopify New Customer Revenue

Populate the **New_Customer_Forecast_v2** tab in the Havn Financial Model by reading 24 months of funnel data, calculating base metrics and seasonal indices, and writing SUMPRODUCT formulas for all historical months. Then set up the forecast framework so the user only needs to input future ad spend to see projected revenue.

## When to Use

- User says "run the forecast," "populate the forecast tab," "financial forecast," "new customer forecast," "Havn forecast," "revenue forecast," or similar
- User wants to update the Havn Financial Model with latest funnel data
- User asks about projected new customer revenue or CAC/AOV trends

## MCP Tool Reference

Only 4 tools are needed. Every tool name below is the exact callable name — use `ToolSearch` with `select:` to load each before first use.

| Tool | Purpose |
|------|---------|
| `mcp__claude_ai_gsheets-mcp__read_range` | Read a single range from the spreadsheet |
| `mcp__claude_ai_gsheets-mcp__batch_read` | Read multiple ranges in one call |
| `mcp__claude_ai_gsheets-mcp__write_range` | Write values or formulas to a single range |
| `mcp__claude_ai_gsheets-mcp__batch_write` | Write values or formulas to multiple ranges |

**Load tools before use:**
```
Call ToolSearch with query: "+gsheets read_range"
Call ToolSearch with query: "+gsheets batch_read"
Call ToolSearch with query: "+gsheets write_range"
Call ToolSearch with query: "+gsheets batch_write"
```

## Spreadsheet Reference

| Item | Value |
|------|-------|
| Spreadsheet ID | `1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8` |
| Spreadsheet Name | Havn - Financial Model v1 |
| Source Tab | `24-Month-Funnel` |
| Target Tab | `New_Customer_Forecast_v2` |

### 24-Month-Funnel Tab — Column Map

| Column | Header | Use |
|--------|--------|-----|
| A | Week Start | Date key for SUMPRODUCT matching |
| B | Week End | — |
| P | Total Cost (USD) | Weekly ad spend (Meta + Google) |
| AA | Net sales | Weekly revenue |
| AB | Orders | Weekly order count |
| AD | AOV | Weekly avg order value |
| AE | New Customers | Weekly new customer count |
| AO | CAC | Weekly cost per acquisition |

- Data lives in rows 2–103 (~100 weeks, Jan 2024 – Dec 2025)
- Read up to row 200 to be safe for future data additions

### New_Customer_Forecast_v2 Tab — Cell Map

| Cell(s) | Content |
|---------|---------|
| B11 | Base CAC (calculated from recent 3 months) |
| B12 | Base AOV (calculated from recent 3 months) |
| B16:M16 | Month names (Jan–Dec) |
| B17:M17 | Month numbers (1–12) |
| B18:M18 | CAC Efficiency Index (seasonal multiplier per calendar month) |
| B19:M19 | AOV Index (seasonal multiplier per calendar month) |
| A22:A26 | Spend level thresholds (dollar amounts) |
| B22:B26 | CAC inflator values (diminishing returns at scale) |
| Row 29 | Month-end dates: B29=Jan 31 2024 … M29=Dec 2024 … N29=Jan 2025 … Y29=Dec 2025 … Z29=Jan 2026 (first forecast month) |
| Row 31 | Monthly Ad Spend |
| Row 32 | CAC |
| Row 33 | New Customers Acquired |
| Row 34 | New Customer AOV |
| Row 36 | New Customer Revenue (= row 33 × row 34, formulas already exist) |
| Row 38 | RETURNING CUSTOMER REVENUE (section header, future phase) |

**Column mapping for rows 29–36:**
- B = Jan 2024, C = Feb 2024, … M = Dec 2024
- N = Jan 2025, O = Feb 2025, … Y = Dec 2025
- Z = Jan 2026 (first forecast month), AA = Feb 2026, …

## Step-by-Step Workflow

### Step 1: Read & Analyze the 24-Month Funnel

Read the source data in a single batch call.

```
Call mcp__claude_ai_gsheets-mcp__batch_read
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  ranges: [
    "24-Month-Funnel!A2:A200",
    "24-Month-Funnel!P2:P200",
    "24-Month-Funnel!AA2:AA200",
    "24-Month-Funnel!AB2:AB200",
    "24-Month-Funnel!AE2:AE200"
  ]
```

This returns:
- Column A: Week Start dates (use for month/year matching)
- Column P: Total Cost (USD) — weekly ad spend
- Column AA: Net sales — weekly revenue
- Column AB: Orders — weekly order count
- Column AE: New Customers — weekly new customer count

**Present to user:**
- Date range covered (e.g., "Jan 2024 – Dec 2025, 100 weeks of data")
- Monthly spend trend (increasing? stable?)
- New customer trend
- CAC trend (spend / new customers)
- AOV trend (revenue / orders)
- Any notable anomalies (zero weeks, spikes, drops)

Wait for user acknowledgment before proceeding.

### Step 2: Calculate & Write Base CAC

Filter funnel data for the **3 most recent months** (Oct–Dec 2025 based on Week Start dates).

**Calculation:**
```
Base CAC = SUM(Total Cost for Oct–Dec 2025 weeks) / SUM(New Customers for Oct–Dec 2025 weeks)
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B11"
  values: [[{calculated_base_cac}]]
```

Tell user: "Base CAC set to ${X} based on Oct–Dec 2025 data (total spend ${Y} / {Z} new customers)."

### Step 3: Calculate & Write Base AOV

Same 3-month window (Oct–Dec 2025).

**Calculation:**
```
Base AOV = SUM(Net Sales for Oct–Dec 2025 weeks) / SUM(Orders for Oct–Dec 2025 weeks)
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B12"
  values: [[{calculated_base_aov}]]
```

Tell user: "Base AOV set to ${X} based on Oct–Dec 2025 data (total revenue ${Y} / {Z} orders)."

### Step 4: Calculate & Write AOV Seasonal Index

For each calendar month (1–12), compute the weighted average AOV across all available years.

**Calculation for each month M (1–12):**
```
Month_AOV(M) = SUM(Net Sales where MONTH(Week Start) = M) / SUM(Orders where MONTH(Week Start) = M)
Overall_Avg_AOV = SUM(all Net Sales) / SUM(all Orders)
AOV_Index(M) = Month_AOV(M) / Overall_Avg_AOV
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B19:M19"
  values: [[{jan_index}, {feb_index}, ..., {dec_index}]]
```

Tell user the seasonal AOV indices. Highlight months with highest/lowest indices and explain the seasonality pattern.

### Step 5: Calculate & Write CAC Seasonal Index

For each calendar month (1–12), compute the weighted average CAC.

**Calculation for each month M (1–12):**
```
Month_CAC(M) = SUM(Ad Spend where MONTH(Week Start) = M) / SUM(New Customers where MONTH(Week Start) = M)
Overall_Avg_CAC = SUM(all Ad Spend) / SUM(all New Customers)
CAC_Index(M) = Month_CAC(M) / Overall_Avg_CAC
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B18:M18"
  values: [[{jan_index}, {feb_index}, ..., {dec_index}]]
```

Tell user the seasonal CAC indices. Highlight expensive vs. efficient months.

### Step 5.1: Calculate & Write Spend Level Inflator Table

The inflator table models diminishing returns: as you scale ad spend beyond the current baseline, each additional dollar costs more per acquisition.

**Calculation:**
```
Base_Monthly_Spend = average monthly ad spend for the 3 most recent months (Oct–Dec 2025)
```

Generate 5 tiers:

| Threshold | Inflator | Logic |
|-----------|----------|-------|
| $0 – Base | 1.00 | Current efficiency |
| Base × 1.25 | 1.05 | +25% spend → 5% less efficient |
| Base × 1.50 | 1.12 | +50% spend → 12% less efficient |
| Base × 1.75 | 1.22 | +75% spend → 22% less efficient |
| Base × 2.00 | 1.35 | 2× spend → 35% less efficient |

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!A22:B26"
  values: [
    [{threshold_1}, 1.00],
    [{threshold_2}, 1.05],
    [{threshold_3}, 1.12],
    [{threshold_4}, 1.22],
    [{threshold_5}, 1.35]
  ]
```

Present the inflator table to the user and ask: "These are the default diminishing-returns assumptions. Want to adjust any of the inflator values before I proceed?"

Wait for confirmation before continuing.

### Step 6: Write SUMPRODUCT Formulas — Monthly Ad Spend (Historicals)

Write formulas to **row 31, columns B through Y** (24 historical months: Jan 2024 – Dec 2025).

**Formula pattern** (example for cell B31, which corresponds to Jan 2024):
```
=SUMPRODUCT(('24-Month-Funnel'!$P$2:$P$200)*(MONTH('24-Month-Funnel'!$A$2:$A$200)=MONTH(B29))*(YEAR('24-Month-Funnel'!$A$2:$A$200)=YEAR(B29)))
```

Each cell references its own row-29 date for month/year matching.

**Build the formula array:**
```python
# Columns B through Y = 24 cells
columns = ["B","C","D","E","F","G","H","I","J","K","L","M",
           "N","O","P","Q","R","S","T","U","V","W","X","Y"]
formulas = []
for col in columns:
    formulas.append(
        f"=SUMPRODUCT(('24-Month-Funnel'!$P$2:$P$200)*(MONTH('24-Month-Funnel'!$A$2:$A$200)=MONTH({col}29))*(YEAR('24-Month-Funnel'!$A$2:$A$200)=YEAR({col}29)))"
    )
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B31:Y31"
  values: [[{formula_B}, {formula_C}, ..., {formula_Y}]]
  valueInputOption: "USER_ENTERED"
```

**IMPORTANT:** The `valueInputOption` must be `USER_ENTERED` so Google Sheets interprets these as formulas, not literal text.

### Step 7: Write SUMPRODUCT Formulas — New Customers (Historicals)

Same pattern for **row 33**, using column AE (New Customers) instead of P.

**Formula pattern** (example for cell B33):
```
=SUMPRODUCT(('24-Month-Funnel'!$AE$2:$AE$200)*(MONTH('24-Month-Funnel'!$A$2:$A$200)=MONTH(B29))*(YEAR('24-Month-Funnel'!$A$2:$A$200)=YEAR(B29)))
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B33:Y33"
  values: [[{formula_B}, {formula_C}, ..., {formula_Y}]]
  valueInputOption: "USER_ENTERED"
```

### Step 8: Write Historical CAC Formulas

**Row 32, columns B through Y.** Simple division: ad spend / new customers.

**Formula pattern** (example for cell B32):
```
=IF(B33>0, B31/B33, "")
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B32:Y32"
  values: [[
    "=IF(B33>0,B31/B33,\"\")", "=IF(C33>0,C31/C33,\"\")", "=IF(D33>0,D31/D33,\"\")",
    "=IF(E33>0,E31/E33,\"\")", "=IF(F33>0,F31/F33,\"\")", "=IF(G33>0,G31/G33,\"\")",
    "=IF(H33>0,H31/H33,\"\")", "=IF(I33>0,I31/I33,\"\")", "=IF(J33>0,J31/J33,\"\")",
    "=IF(K33>0,K31/K33,\"\")", "=IF(L33>0,L31/L33,\"\")", "=IF(M33>0,M31/M33,\"\")",
    "=IF(N33>0,N31/N33,\"\")", "=IF(O33>0,O31/O33,\"\")", "=IF(P33>0,P31/P33,\"\")",
    "=IF(Q33>0,Q31/Q33,\"\")", "=IF(R33>0,R31/R33,\"\")", "=IF(S33>0,S31/S33,\"\")",
    "=IF(T33>0,T31/T33,\"\")", "=IF(U33>0,U31/U33,\"\")", "=IF(V33>0,V31/V33,\"\")",
    "=IF(W33>0,W31/W33,\"\")", "=IF(X33>0,X31/X33,\"\")", "=IF(Y33>0,Y31/Y33,\"\")"
  ]]
  valueInputOption: "USER_ENTERED"
```

### Step 9: Write Historical AOV Formulas

**Row 34, columns B through Y.** Uses SUMPRODUCT to calculate revenue/orders from the funnel.

**Formula pattern** (example for cell B34):
```
=IFERROR(SUMPRODUCT(('24-Month-Funnel'!$AA$2:$AA$200)*(MONTH('24-Month-Funnel'!$A$2:$A$200)=MONTH(B29))*(YEAR('24-Month-Funnel'!$A$2:$A$200)=YEAR(B29)))/SUMPRODUCT(('24-Month-Funnel'!$AB$2:$AB$200)*(MONTH('24-Month-Funnel'!$A$2:$A$200)=MONTH(B29))*(YEAR('24-Month-Funnel'!$A$2:$A$200)=YEAR(B29))),"")
```

**Build the formula array** (same column iteration as Steps 6–7):
```python
for col in columns:
    formulas.append(
        f'=IFERROR(SUMPRODUCT((\'24-Month-Funnel\'!$AA$2:$AA$200)*(MONTH(\'24-Month-Funnel\'!$A$2:$A$200)=MONTH({col}29))*(YEAR(\'24-Month-Funnel\'!$A$2:$A$200)=YEAR({col}29)))/SUMPRODUCT((\'24-Month-Funnel\'!$AB$2:$AB$200)*(MONTH(\'24-Month-Funnel\'!$A$2:$A$200)=MONTH({col}29))*(YEAR(\'24-Month-Funnel\'!$A$2:$A$200)=YEAR({col}29))),"")'
    )
```

**Write:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!B34:Y34"
  values: [[{formula_B}, {formula_C}, ..., {formula_Y}]]
  valueInputOption: "USER_ENTERED"
```

### Step 10: Review & Forecast Discussion

After all historicals are populated, verify and present results.

**Verify — read back the populated rows:**
```
Call mcp__claude_ai_gsheets-mcp__batch_read
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  ranges: [
    "New_Customer_Forecast_v2!B29:Y29",
    "New_Customer_Forecast_v2!B31:Y31",
    "New_Customer_Forecast_v2!B32:Y32",
    "New_Customer_Forecast_v2!B33:Y33",
    "New_Customer_Forecast_v2!B34:Y34",
    "New_Customer_Forecast_v2!B36:Y36"
  ]
```

**Present a summary table to the user:**
```
| Month    | Ad Spend | CAC   | New Customers | AOV   | New Cust Revenue |
|----------|----------|-------|---------------|-------|-----------------|
| Jan 2024 | $X       | $X    | X             | $X    | $X              |
| Feb 2024 | $X       | $X    | X             | $X    | $X              |
| ...      | ...      | ...   | ...           | ...   | ...             |
| Dec 2025 | $X       | $X    | X             | $X    | $X              |
```

Check for:
- Any `#N/A` or `#REF!` errors (means formula references are wrong)
- Any $0 months that should have data (means SUMPRODUCT matching failed)
- Revenue row (36) should equal row 33 × row 34 (formulas already exist)

**Then ask the user:**

> "Historicals are populated. For the forecast months (Jan 2026 onward, column Z+), I need monthly ad spend targets. Options:
> 1. **Flat spend** — same amount every month (tell me the number)
> 2. **Growth trajectory** — start at $X/month and grow Y% monthly
> 3. **Custom** — you specify each month's spend
>
> Once ad spend is entered, the CAC/customers/AOV/revenue formulas will auto-calculate using the seasonal indices and inflator table.
>
> What approach do you want?"

Once the user provides ad spend targets for forecast months:

**Write forecast ad spend:**
```
Call mcp__claude_ai_gsheets-mcp__write_range
  spreadsheet_id: "1K2N8zasZG1mRf_ZVisZlhuQfuwsro4eRyDLc-OEuzL8"
  range: "New_Customer_Forecast_v2!Z31:{end_col}31"
  values: [[{month1_spend}, {month2_spend}, ...]]
```

**Write forecast CAC formulas** (using base CAC × seasonal index × spend inflator):
```
For each forecast month column (Z, AA, AB, ...):
=B11 * VLOOKUP(MONTH({col}29), $B$17:$M$18, 2, FALSE) * {inflator_lookup}
```

The exact inflator lookup formula:
```
=B11 * INDEX($B$18:$M$18, MATCH(MONTH({col}29), $B$17:$M$17, 0)) * INDEX($B$22:$B$26, MATCH(TRUE, $A$22:$A$26>={col}31, 0))
```

**Write forecast new customers:**
```
=IF({col}32>0, {col}31/{col}32, 0)
```

**Write forecast AOV:**
```
=B12 * INDEX($B$19:$M$19, MATCH(MONTH({col}29), $B$17:$M$17, 0))
```

Row 36 (revenue) should auto-calculate from existing formulas (row 33 × row 34).

**Present the projected new customer revenue** and offer to adjust assumptions.

## Verification Checklist

After completing all steps, verify:

- [ ] Base CAC in B11 matches manual calculation
- [ ] Base AOV in B12 matches manual calculation
- [ ] Seasonal indices in B18:M18 and B19:M19 sum to approximately 12.0 (average ~1.0)
- [ ] SUMPRODUCT formulas in rows 31, 33, 34 populate with numbers (not errors)
- [ ] CAC formulas in row 32 = row 31 / row 33
- [ ] Revenue in row 36 = row 33 × row 34
- [ ] No #N/A, #REF!, or #DIV/0! errors in the historical range
- [ ] Forecast formulas chain correctly when ad spend is entered

## Important Notes

- **Always use `valueInputOption: "USER_ENTERED"`** when writing formulas — otherwise Google Sheets stores them as text
- **Date matching uses MONTH() and YEAR() on the Week Start column** — this correctly aggregates weekly data to monthly
- **The inflator table is an assumption** — present it to the user and let them adjust before building forecast formulas that reference it
- **Row 36 (revenue) already has formulas** — do NOT overwrite it. If it's blank, it should be `=row33 * row34`
- **Forecast months start at column Z** — columns B–Y are historicals only
