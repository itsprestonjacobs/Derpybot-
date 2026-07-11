"""
Regenerates the web deliverables from the course markdown.

Run this after editing anything in ../course/ so the pasteable fragments and the
full website stay in sync with the lessons.

    pip install markdown pygments
    python tools/build.py

Outputs:
    ../web/lesson-*.html + troubleshooting.html   (pasteable fragments)
    ../docs/index.html                            (full GitHub Pages site)
"""
import os
import re

import markdown
from pygments.formatters import HtmlFormatter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(BASE, "course")
WEB = os.path.join(BASE, "web")
SITE = os.path.join(BASE, "docs")   # GitHub Pages serves from /docs
for d in (WEB, SITE):
    os.makedirs(d, exist_ok=True)

MODULES = [
    ("Foundations", [
        ("How Discord Bots Work", "01-how-bots-work.md"),
        ("Install Your Tools", "02-tools-setup.md"),
        ("Python: Variables & Types", "03-python-variables.md"),
        ("Python: Lists & Dictionaries", "04-python-collections.md"),
        ("Python: Making Decisions", "05-python-logic.md"),
        ("Python: Loops", "06-python-loops.md"),
        ("Python: Functions", "07-python-functions.md"),
        ("Python: Classes & Objects", "08-python-classes.md"),
        ("Python: Files & Errors", "09-python-files-errors.md"),
        ("Async & Await", "10-async-await.md"),
    ]),
    ("Your Bot Comes Alive", [
        ("Register Your Bot", "11-register-bot.md"),
        ("Intents & Permissions", "12-intents-permissions.md"),
        ("Invite Your Bot", "13-invite-bot.md"),
        ("First Connection", "14-first-connection.md"),
        ("Events", "15-events.md"),
        ("Slash Commands", "16-slash-commands.md"),
        ("Command Arguments", "17-command-arguments.md"),
        ("Organizing with Cogs", "18-cogs.md"),
    ]),
    ("Messages & Embeds", [
        ("Sending Messages & DMs", "19-messages.md"),
        ("Embeds Deep Dive", "20-embeds.md"),
        ("Embed Recipes & Custom Embeds", "embed-recipes.md"),
        ("A Branding System", "21-branding.md"),
    ]),
    ("Interactive UI", [
        ("Buttons & Views", "22-buttons.md"),
        ("Select Menus (Dropdowns)", "23-select-menus.md"),
        ("Modals (Pop-up Forms)", "24-modals.md"),
        ("Persistent Components", "25-persistent-views.md"),
    ]),
    ("Moderation", [
        ("Permissions & Role Hierarchy", "26-permissions-roles.md"),
        ("Kick, Ban & Unban", "27-kick-ban.md"),
        ("Timeout, Purge & Warn", "28-timeout-purge-warn.md"),
        ("More Mod Commands & Adding Your Own", "more-mod-commands.md"),
        ("Welcome & Leave Messages", "29-welcome-leave.md"),
        ("Auto-roles & Reaction Roles", "30-auto-reaction-roles.md"),
        ("Auto-moderation", "31-automod.md"),
        ("A Logging System", "32-logging.md"),
    ]),
    ("Data & Storage", [
        ("Saving Data with JSON", "33-json.md"),
        ("Databases with SQLite", "34-sqlite.md"),
        ("Per-Server Settings", "35-per-server-settings.md"),
    ]),
    ("Projects", [
        ("Project: Ticket System", "36-project-tickets.md"),
        ("Project: Economy & Leveling", "37-project-economy.md"),
    ]),
    ("Going Further", [
        ("Background Tasks & Scheduling", "38-tasks-scheduling.md"),
        ("Cooldowns & Rate Limits", "39-cooldowns.md"),
        ("Error Handling & a Help Command", "40-error-handling-help.md"),
        ("Calling Web APIs & Webhooks", "41-web-apis.md"),
    ]),
    ("Ship It", [
        ("Make It Yours: One-File Setup", "make-it-yours.md"),
        ("Git & GitHub for Your Bot", "42-git-github.md"),
        ("Host It 24/7", "43-hosting.md"),
        ("Wrap-up & Next Steps", "44-wrap-up.md"),
    ]),
    ("Help", [
        ("Troubleshooting", "troubleshooting.md"),
    ]),
]

# Flatten into (lid, num, title, src, out, module).
LESSONS = []
_i = 0
for _module, _items in MODULES:
    for _title, _src in _items:
        _i += 1
        _num = "?" if _src == "troubleshooting.md" else f"{_i:02d}"
        LESSONS.append((f"l{_i}", _num, _title, _src, _src.replace(".md", ".html"), _module))

# Dark code theme so code reads the same in both site themes (Discord-like).
try:
    _fmt = HtmlFormatter(style="one-dark")
except Exception:
    _fmt = HtmlFormatter(style="monokai")
PYG = _fmt.get_style_defs(".ddc .codehilite")

md = markdown.Markdown(extensions=["fenced_code", "tables", "codehilite", "sane_lists"],
                       extension_configs={"codehilite": {"guess_lang": False}})


def convert(path):
    md.reset()
    with open(os.path.join(COURSE, path), encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"^[←→].*$", "", text, flags=re.MULTILINE)  # drop md nav arrows
    return md.convert(text)


# ---------- flat content styling (.ddc) — no gradients, solid accent ----------
CONTENT_CSS = """
.ddc h1{font-size:1.95rem;line-height:1.2;margin:.1em 0 .15em;letter-spacing:-.01em;color:var(--strong);font-weight:800;}
.ddc h2{font-size:1.35rem;margin:1.9em 0 .5em;padding-top:1em;border-top:1px solid var(--border);color:var(--strong);font-weight:700;}
.ddc h3{font-size:1.1rem;margin:1.5em 0 .35em;color:var(--strong);font-weight:700;}
.ddc p,.ddc li{font-size:1.005rem;}
.ddc a{color:var(--accent);font-weight:600;text-decoration:none;}
.ddc a:hover{text-decoration:underline;}
.ddc strong{color:var(--strong);font-weight:700;}
.ddc hr{border:0;height:1px;background:var(--border);margin:2.1em 0;}
.ddc ul,.ddc ol{padding-left:1.3em;}.ddc li{margin:.3em 0;}
.ddc :not(pre)>code{background:var(--code-inline);color:var(--code-inline-fg);padding:.12em .4em;border-radius:4px;font-size:.9em;font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;}
.ddc table{border-collapse:collapse;width:100%;margin:1.1em 0;font-size:.93rem;display:block;overflow-x:auto;}
.ddc th,.ddc td{border:1px solid var(--border);padding:.55em .75em;text-align:left;}
.ddc th{background:var(--panel);color:var(--strong);font-weight:700;}
.ddc blockquote{margin:1.25em 0;padding:.8em 1em;border-left:3px solid var(--accent);background:var(--accent-weak);border-radius:0 4px 4px 0;}
.ddc blockquote.warn{border-left-color:var(--warn);background:var(--warn-weak);}
.ddc blockquote.good{border-left-color:var(--good);background:var(--good-weak);}
.ddc blockquote p{margin:.3em 0;}
.ddc .codehilite{position:relative;background:var(--code-bg);border:1px solid var(--code-border);border-radius:6px;margin:1.1em 0;}
.ddc .codehilite pre{margin:0;padding:14px 15px;overflow-x:auto;font-size:.875rem;line-height:1.55;font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;}
.ddc .copy-btn{position:absolute;top:7px;right:7px;background:rgba(255,255,255,.07);color:#cdd6e4;border:1px solid rgba(255,255,255,.14);border-radius:5px;font-size:.72rem;padding:3px 9px;cursor:pointer;font-weight:700;opacity:0;transition:opacity .12s;}
.ddc .codehilite:hover .copy-btn,.ddc .copy-btn:focus{opacity:1;}
.ddc .copy-btn:hover{background:var(--accent);color:#fff;border-color:var(--accent);}
.ddc .copy-btn.done{background:var(--good);color:#fff;border-color:var(--good);opacity:1;}
""" + PYG

ENHANCE_JS = r"""
(function(){
 function enhance(){
  document.querySelectorAll('.ddc .codehilite:not([data-cp])').forEach(function(box){
   box.setAttribute('data-cp','1');
   var b=document.createElement('button');b.className='copy-btn';b.type='button';b.textContent='Copy';
   b.addEventListener('click',function(){navigator.clipboard.writeText(box.querySelector('pre').innerText).then(function(){
    b.textContent='Copied';b.classList.add('done');setTimeout(function(){b.textContent='Copy';b.classList.remove('done');},1300);});});
   box.appendChild(b);});
  document.querySelectorAll('.ddc blockquote:not([data-cl])').forEach(function(q){
   q.setAttribute('data-cl','1');var c=q.textContent.trim().charAt(0);
   if(c==='⚠')q.classList.add('warn');else if(c==='✅')q.classList.add('good');});
 }
 if(document.readyState!=='loading')enhance();else document.addEventListener('DOMContentLoaded',enhance);
})();
"""

# Token blocks shared by fragments and site.
TOKENS_LIGHT = ("--bg:#ffffff;--panel:#f5f6f8;--sidebar:#f4f5f7;--text:#333a42;--dim:#5c6773;"
                "--strong:#111318;--border:#e2e4e8;--accent:#4752c4;--accent-weak:#ecedfb;"
                "--good:#1a7f4b;--good-weak:#e7f4ec;--warn:#8a5a00;--warn-weak:#fbf1de;"
                "--code-inline:#eef1f5;--code-inline-fg:#0b5fb0;--code-bg:#1e2127;--code-border:#2b303a;--card:#ffffff;")
TOKENS_DARK = ("--bg:#1e1f22;--panel:#26282c;--sidebar:#1a1b1e;--text:#cfd4db;--dim:#8b939f;"
               "--strong:#f2f3f5;--border:#34373d;--accent:#5865f2;--accent-weak:rgba(88,101,242,.16);"
               "--good:#3ba55d;--good-weak:rgba(59,165,93,.14);--warn:#d6a025;--warn-weak:rgba(214,160,37,.14);"
               "--code-inline:#2b2d31;--code-inline-fg:#8fd0ff;--code-bg:#1a1b1e;--code-border:#34373d;--card:#26282c;")


# ================= 1) pasteable fragments =================
FRAG_STYLE = ("<style>\n.ddc{" + TOKENS_LIGHT +
              "font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;line-height:1.65;"
              "color:var(--text);max-width:820px;margin:0 auto;padding:8px 4px 40px;}\n"
              ".ddc *{box-sizing:border-box;}\n"
              "@media (prefers-color-scheme:dark){.ddc{" + TOKENS_DARK + "}}\n"
              + CONTENT_CSS + "\n</style>")
FRAG_SCRIPT = "<script>\n" + ENHANCE_JS + "\n</script>"

for lid, num, title, src, out, module in LESSONS:
    body = convert(src)
    frag = f'<section class="ddc">\n{body}\n</section>\n{FRAG_STYLE}\n{FRAG_SCRIPT}\n'
    with open(os.path.join(WEB, out), "w", encoding="utf-8") as f:
        f.write(frag)
print(f"web/      {len(LESSONS)} fragments")


# ================= 2) full site =================
side, arts = [], []
n = len(LESSONS)
current_module = None
for i, (lid, num, title, src, out, module) in enumerate(LESSONS):
    body = convert(src)
    prev = (f'<a class="pn prev" href="#{LESSONS[i-1][0]}"><span>Previous</span>'
            f'<b>{LESSONS[i-1][2]}</b></a>') if i > 0 else '<span></span>'
    nxt = (f'<a class="pn next" href="#{LESSONS[i+1][0]}"><span>Next</span>'
           f'<b>{LESSONS[i+1][2]}</b></a>') if i < n - 1 else ''
    arts.append(f'<article class="ddc lesson" id="{lid}" data-idx="{i}">\n{body}\n'
                f'<nav class="pn-row">{prev}{nxt}</nav>\n</article>')
    if module != current_module:
        side.append(f'<div class="side-group">{module}</div>')
        current_module = module
    side.append(f'<a class="nav-link" href="#{lid}" data-target="{lid}">'
                f'<span class="nav-num">{num}</span><span class="nav-title">{title}</span></a>')

SITE_STYLE = """
<style>
:root{__L__}
@media (prefers-color-scheme:dark){:root{__D__}}
:root[data-theme="dark"]{__D__}
:root[data-theme="light"]{__L__}
*{box-sizing:border-box;}html{scroll-behavior:smooth;}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.65;}
a{color:var(--accent);}
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;height:56px;padding:0 18px;background:var(--sidebar);border-bottom:1px solid var(--border);}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;}
.logo{width:32px;height:32px;border-radius:7px;background:var(--accent);display:grid;place-items:center;color:#fff;font-weight:900;font-size:1.05rem;}
.brand small{display:block;font-weight:600;font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:var(--dim);margin-top:1px;}
.spacer{flex:1;}
.theme-btn{background:transparent;border:1px solid var(--border);color:var(--text);border-radius:7px;height:36px;width:36px;font-size:1rem;cursor:pointer;display:grid;place-items:center;}
.theme-btn:hover{border-color:var(--accent);color:var(--accent);}
.wrap{display:grid;grid-template-columns:256px minmax(0,1fr);max-width:1160px;margin:0 auto;}
.sidebar{position:sticky;top:56px;align-self:start;height:calc(100vh - 56px);overflow-y:auto;padding:18px 12px;background:var(--sidebar);border-right:1px solid var(--border);}
.side-label{font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:var(--dim);font-weight:700;padding:0 10px 8px;}
.side-group{font-size:.64rem;letter-spacing:.11em;text-transform:uppercase;color:var(--accent);font-weight:800;padding:14px 10px 5px;margin-top:4px;border-top:1px solid var(--border);}
.side-group:first-of-type{border-top:0;margin-top:0;}
.nav-link{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:6px;text-decoration:none;color:var(--text);font-size:.92rem;font-weight:600;margin-bottom:1px;}
.nav-link:hover{background:var(--accent-weak);}
.nav-link.active{background:var(--accent);color:#fff;}
.nav-num{flex:none;width:25px;height:25px;border-radius:5px;display:grid;place-items:center;font-size:.76rem;font-weight:800;background:var(--accent-weak);color:var(--accent);font-variant-numeric:tabular-nums;}
.nav-link.active .nav-num{background:rgba(255,255,255,.22);color:#fff;}
.nav-title{flex:1;}
.progress{margin:16px 10px 4px;}
.progress-bar{height:5px;border-radius:99px;background:var(--border);overflow:hidden;}
.progress-fill{height:100%;width:0;background:var(--accent);transition:width .25s;}
.progress-txt{font-size:.71rem;color:var(--dim);margin-top:6px;}
.content{padding:32px 44px 84px;min-width:0;}
.lesson{display:none;}.lesson.active{display:block;}
.ddc{max-width:720px;}
.pn-row{display:flex;justify-content:space-between;gap:14px;margin-top:3em;padding-top:1.4em;border-top:1px solid var(--border);}
.pn{display:flex;flex-direction:column;gap:2px;text-decoration:none;padding:11px 15px;border:1px solid var(--border);border-radius:7px;min-width:145px;background:var(--card);}
.pn:hover{border-color:var(--accent);}
.pn.next{text-align:right;margin-left:auto;}
.pn span{font-size:.7rem;color:var(--dim);text-transform:uppercase;letter-spacing:.07em;font-weight:700;}
.pn b{color:var(--strong);font-size:.95rem;}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
__CONTENT__
@media(max-width:900px){.wrap{grid-template-columns:1fr;}.sidebar{position:static;height:auto;border-right:0;border-bottom:1px solid var(--border);display:flex;gap:6px;overflow-x:auto;padding:10px;}.side-label,.side-group,.progress{display:none;}.nav-link{flex:none;margin:0;white-space:nowrap;}.nav-title{display:none;}.nav-num{width:auto;padding:0 8px;height:27px;}.content{padding:22px 16px 64px;}.ddc h1{font-size:1.6rem;}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto;}}
</style>
""".replace("__L__", TOKENS_LIGHT).replace("__D__", TOKENS_DARK).replace("__CONTENT__", CONTENT_CSS)

SITE_SCRIPT = ("""
<script>
(function(){
 var links=[].slice.call(document.querySelectorAll('.nav-link'));
 var ids=links.map(function(l){return l.dataset.target;});
 var done=JSON.parse(localStorage.getItem('ddc_done')||'[]');
 function paint(){links.forEach(function(l){if(done.indexOf(l.dataset.target)>-1)l.classList.add('done');});
  var pct=Math.round(done.length/links.length*100);var f=document.querySelector('.progress-fill');var t=document.querySelector('.progress-txt');
  if(f)f.style.width=pct+'%';if(t)t.textContent=done.length+' of '+links.length+' lessons visited';}
 function show(id){if(ids.indexOf(id)<0)id=ids[0];
  document.querySelectorAll('.lesson').forEach(function(a){a.classList.toggle('active',a.id===id);});
  links.forEach(function(l){l.classList.toggle('active',l.dataset.target===id);});
  if(done.indexOf(id)<0){done.push(id);localStorage.setItem('ddc_done',JSON.stringify(done));}
  paint();window.scrollTo(0,0);}
 __ENHANCE__
 var root=document.documentElement;var saved=localStorage.getItem('ddc_theme');if(saved)root.setAttribute('data-theme',saved);
 var tb=document.querySelector('.theme-btn');
 function icon(){var d=root.getAttribute('data-theme');var dark=d?d==='dark':matchMedia('(prefers-color-scheme:dark)').matches;tb.textContent=dark?'☀':'☾';}
 if(tb){tb.addEventListener('click',function(){var d=root.getAttribute('data-theme');var dark=d?d==='dark':matchMedia('(prefers-color-scheme:dark)').matches;var nx=dark?'light':'dark';root.setAttribute('data-theme',nx);localStorage.setItem('ddc_theme',nx);icon();});icon();matchMedia('(prefers-color-scheme:dark)').addEventListener('change',icon);}
 window.addEventListener('hashchange',function(){show(location.hash.replace('#',''));});
 paint();show((location.hash||'').replace('#','')||ids[0]);
})();
</script>
""").replace("__ENHANCE__", ENHANCE_JS.strip())

TOPBAR = ('<header class="topbar"><div class="brand"><div class="logo">&gt;_</div>'
          '<div>Discord Bot Course<small>Python &middot; discord.py</small></div></div>'
          '<div class="spacer"></div>'
          '<button class="theme-btn" type="button" aria-label="Toggle light or dark theme">&#9790;</button></header>')
BODY = (TOPBAR + '<div class="wrap"><aside class="sidebar"><div class="side-label">Lessons</div>'
        + "\n".join(side) +
        '<div class="progress"><div class="progress-bar"><div class="progress-fill"></div></div>'
        '<div class="progress-txt"></div></div></aside><main class="content">'
        + "\n".join(arts) + '</main></div>')

index_html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
              '<title>Discord Bot Course — Python &amp; discord.py</title>\n'
              '<meta name="description" content="Build a Python Discord bot from scratch — embeds, moderation, and a ticket system.">\n'
              + SITE_STYLE + '\n</head>\n<body>\n' + BODY + '\n' + SITE_SCRIPT + '\n</body>\n</html>\n')
with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
# A .nojekyll file tells GitHub Pages to serve the folder as-is.
open(os.path.join(SITE, ".nojekyll"), "w").close()
print("docs/     index.html")
print("DONE")
