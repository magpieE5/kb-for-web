Audits Knowledge Base

KB health check and curation.

## Execution

Run all checks, surface top issues for discussion.

**1. Stats**

```bash
kb query "SELECT category, COUNT(*) as cnt FROM kb_knowledge GROUP BY category ORDER BY cnt DESC"
kb query "SELECT id, category, length(content) as chars, updated FROM kb_knowledge ORDER BY updated DESC LIMIT 10"
kb query "SELECT id, category, length(content) as chars FROM kb_knowledge ORDER BY chars DESC LIMIT 10"
```

**2. Staleness**

Entries not updated in 30+ days that aren't reference material:

```bash
kb query "SELECT id, category, updated FROM kb_knowledge WHERE updated < CURRENT_DATE - 30 AND category NOT IN ('reference', 'seed', 'log', 'transcript') ORDER BY updated ASC LIMIT 20"
```

**3. Fragmentation**

Similar titles that could be consolidated (character n-gram similarity):

```bash
kb query "SELECT a.id, b.id as similar_id, a.category, jaccard(lower(a.title), lower(b.title)) as sim FROM kb_knowledge a JOIN kb_knowledge b ON a.id < b.id AND a.category = b.category WHERE a.category NOT IN ('log', 'transcript', 'seed') AND jaccard(lower(a.title), lower(b.title)) > 0.6 ORDER BY sim DESC LIMIT 20"
```

**4. Mode coverage**

Entries that should be in modes but aren't:

```bash
kb query "SELECT id, category, title FROM kb_knowledge WHERE category IN ('pattern', 'reference') AND id NOT IN (SELECT id FROM kb_mode) ORDER BY category, id LIMIT 20"
```

**5. Corrections**

```bash
kb get accumulator-corrections
```

For each: update the source KB entry, then delete the correction. Goal: empty accumulator.

**6. Logs**

```bash
kb query "SELECT id FROM kb_knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT 5"
```

Then load each via `kb get {id}`. Look for recurring handoff items and repeated themes.

---

## How to work through issues

1. **Surface** — Query and display issues
2. **Discuss** — One issue at a time
3. **Fix** — Update KB in-session, don't defer
4. **Verify** — Confirm fix addresses the issue
5. **Next** — Move to next issue or close

A thorough audit of 3 issues beats a shallow pass over 30.
