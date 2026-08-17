"""Add deep-linking (?reality=&epoch=&zone=) and an embed mode (?embed=1) to the viewer.

Embed mode hides the page header chrome so the twin can sit in an <iframe> on another site
(e.g. winniio.io) and still be the same artefact — one build, no fork.

python scripts/patch_embed.py
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
p = os.path.join(ROOT, "site", "template.html")
s = open(p, encoding="utf-8").read()

s = s.replace("footer{padding:12px 22px 28px;color:var(--muted);font-size:12px}",
              "footer{padding:12px 22px 28px;color:var(--muted);font-size:12px}\n"
              "body.embed h1 small,body.embed .reality-h{display:none}\n"
              "body.embed header{padding-top:10px}\n"
              "body.embed footer{padding:8px 22px 14px}\n"
              ".permalink{font-size:12px;color:var(--muted);margin-left:auto}\n"
              ".permalink button{padding:4px 8px;font-size:12px}")

s = s.replace('''    <label><input type="checkbox" id="pipeonly"> Pipeline only (remiss / NWP)</label>''',
              '''    <label><input type="checkbox" id="pipeonly"> Pipeline only (remiss / NWP)</label>
    <span class="permalink"><button id="copylink" type="button" title="Copy a link to exactly this view">Copy link to this view</button></span>''')

# state → URL, URL → state
s = s.replace("let epoch = 'now', current = null, selectedKey = null;",
              """let epoch = 'now', current = null, selectedKey = null;
const PARAMS = new URLSearchParams(location.search);
if (PARAMS.get('embed') === '1') document.body.classList.add('embed');
function syncUrl() {
  const q = new URLSearchParams(location.search);
  q.set('reality', sel.value); q.set('epoch', epoch);
  if (selectedKey) q.set('zone', selectedKey); else q.delete('zone');
  history.replaceState(null, '', location.pathname + '?' + q.toString());
}""")

s = s.replace("drawPicker();\ndraw();",
              """if (PARAMS.get('reality') && DATA.realities[PARAMS.get('reality')]) sel.value = PARAMS.get('reality');
if (['past', 'now', 'future'].includes(PARAMS.get('epoch'))) {
  epoch = PARAMS.get('epoch');
  document.querySelectorAll('.seg button').forEach(x => x.setAttribute('aria-pressed', x.dataset.e === epoch ? 'true' : 'false'));
}
if (PARAMS.get('zone')) selectedKey = PARAMS.get('zone');
document.getElementById('copylink').onclick = async () => {
  syncUrl();
  try { await navigator.clipboard.writeText(location.href); document.getElementById('copylink').textContent = 'Copied'; setTimeout(() => document.getElementById('copylink').textContent = 'Copy link to this view', 1500); }
  catch (e) { prompt('Copy this link', location.href); }
};
drawPicker();
draw();""")

# call syncUrl on every state change
s = s.replace("document.querySelectorAll('.seg button').forEach(b => b.onclick = () => { epoch = b.dataset.e; document.querySelectorAll('.seg button').forEach(x => x.setAttribute('aria-pressed', x === b ? 'true' : 'false')); draw(); });",
              "document.querySelectorAll('.seg button').forEach(b => b.onclick = () => { epoch = b.dataset.e; document.querySelectorAll('.seg button').forEach(x => x.setAttribute('aria-pressed', x === b ? 'true' : 'false')); draw(); syncUrl(); });")
s = s.replace("sel.onchange = () => { selectedKey = null; $('dtitle').textContent = 'Select a zone or system'; $('dbody').innerHTML = ''; drawPicker(); draw(); };",
              "sel.onchange = () => { selectedKey = null; $('dtitle').textContent = 'Select a zone or system'; $('dbody').innerHTML = ''; drawPicker(); draw(); syncUrl(); };")
s = s.replace("g.addEventListener('click', () => { selectedKey = 'z:' + z.id; draw(); });",
              "g.addEventListener('click', () => { selectedKey = 'z:' + z.id; draw(); syncUrl(); });")
s = s.replace("b.onclick = () => { selectedKey = 's:' + s.id; draw(); };",
              "b.onclick = () => { selectedKey = 's:' + s.id; draw(); syncUrl(); };")

open(p, "w", encoding="utf-8").write(s)
print("embed + deep-link patched")
