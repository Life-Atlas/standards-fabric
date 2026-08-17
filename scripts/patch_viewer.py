"""Viewer patch: label the basis chip in words, link every document, add a tag legend.

Run once: python scripts/patch_viewer.py  (kept in the repo so the change is reviewable, per
feedback_patch_scripts_in_repo_not_temp).
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
p = os.path.join(ROOT, "site", "template.html")
s = open(p, encoding="utf-8").read()

# 1) basis chip → human words + tooltip; and the doc line always links
old_doc = s[s.index("function docLine(id) {"):s.index("function curLine(id) {")]
new_doc = '''function docLine(id) {
  const d = DOCS[id]; const tags = [];
  const BASIS = {
    'sek-dates': ['dates', "In force in this epoch according to SEK's own fastställande/upphävande dates."],
    'name-year-heuristic': ['year in number', 'International document — the catalogue carries no withdrawal date, so the year in the document number decides. A heuristic, not a verdict.'],
    'status': ['published', 'Published in the catalogue today, with no annulment date.'],
    'pipeline': ['in progress', 'Out for comment, under development or proposed as new work — not yet a standard.'],
    'n/a': ['no date', 'The catalogue gives neither dates nor a year in the number, so this epoch cannot be decided.']
  };
  const b = (d.b || {})[epoch] || 'n/a';
  const [label, tip] = BASIS[b] || [b, ''];
  if (epoch === 'future' && d.pipe) tags.push(`<span class="tag pipe" title="Status in the SEK catalogue">${esc((d.s || '').replace(/_/g, ' '))}</span>`);
  if (epoch === 'future' && d.age) tags.push('<span class="tag age" title="Latest edition is 20+ years old by the future epoch and no revision is in the pipeline — expect a revision or a withdrawal.">aging</span>');
  tags.push(`<span class="tag" title="${esc(tip)}">basis: ${esc(label)}</span>`);
  const name = d.n || (d.t ? '(draft) ' + d.t : id);
  const url = d.u || ('https://elstandard.se/standard/' + id);
  return `<li><a href="${esc(url)}" target="_blank" rel="noopener">${esc(name)}</a> <span class="m">${esc(d.t || '')}${d.y ? ' · ' + d.y : ''} · ${esc(d.c || '')}${d.i ? ' ← ' + esc(d.i) : ''}</span>${tags.join('')}</li>`;
}
'''
s = s.replace(old_doc, new_doc)

# 2) curated line: same treatment for the epoch-state chip
s = s.replace(
    '''<span class="tag">${esc(c.epochs[epoch])}</span>''',
    '''<span class="tag" title="State of this reference in the selected epoch">${esc(c.epochs[epoch])}</span>''')

# 3) legend under the detail panel header
s = s.replace(
    '''    <div id="dbody" class="muted">Counts per epoch appear here; expand a topic to see the documents, with their basis (SEK dates / heuristic / pipeline) and confidence.</div>''',
    '''    <p class="legendbar">Every entry links to its catalogue page. Chips: <span class="tag">basis: …</span> how the epoch verdict was reached (hover for the rule) · <span class="tag pipe">remiss / new work proposal</span> not yet a standard · <span class="tag age">aging</span> 20+ years without a revision · <span class="tag assumed">assumed</span> curated reference not re-verified against a primary source.</p>
    <div id="dbody" class="muted">Pick a zone on the floor plan or a system chip. You get the count per epoch, the delta, and every applicable document grouped by topic.</div>''')

# 4) style for the legend bar
s = s.replace(".basis{font-size:13px;color:var(--muted);margin:4px 0 0}",
              ".basis{font-size:13px;color:var(--muted);margin:4px 0 0}\n.legendbar{font-size:12px;color:var(--muted);margin:0 0 10px;line-height:1.8}")

open(p, "w", encoding="utf-8").write(s)
print("viewer patched")
