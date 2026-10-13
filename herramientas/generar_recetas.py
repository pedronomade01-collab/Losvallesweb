"""Genera recetas.html y recetas/<slug>.html a partir de contenido/recetas.json.

Uso: python3 herramientas/generar_recetas.py
"""
import html
import json
import os
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WA = "573103742028"

with open(os.path.join(RAIZ, "contenido", "recetas.json"), encoding="utf-8") as f:
    RECETAS = json.load(f)

GRUPOS = ["Bebidas", "Desayunos y snacks", "Repostería", "Cocina salada"]


def e(t):
    return html.escape(str(t), quote=True)


def categoria_producto(nombre):
    n = nombre.lower()
    if "aromática" in n:
        return "Aromáticas"
    if "infusión" in n or "mayonesa" in n or "4&co" in n:
        return "4&CO"
    if "tomate" in n:
        return "Tomates"
    if "rodajas de" in n:
        return "Limón y naranja"
    return "Frutas"


def fmt_tiempo(m):
    if m < 60:
        return f"{m} min"
    h, r = divmod(m, 60)
    return f"{h} h" + (f" {r} min" if r else "")


def rango_tiempo(m):
    if m < 15:
        return "rapida"
    if m <= 45:
        return "media"
    return "larga"


CSS = """
:root{
  --bg:#0F1F16; --bg-2:#132820; --surface:#1A3326;
  --ink:#F3EDE0; --muted:#B8B9A9; --line:#2C4636;
  --gold:#C9A45C; --gold-soft:#E3C88E; --on-gold:#0F1F16;
  --pend-bg:#3A3018; --pend-ink:#F1D58C; --pend-line:#8F7330;
  --wa:#25A55A;
  --font:'Roboto','Helvetica Neue',Arial,system-ui,sans-serif;
  --r:4px; color-scheme:dark;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font);font-size:1.02rem;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit}
p{margin:0}
h1,h2,h3{font-family:var(--font);font-style:italic;font-weight:300;line-height:1.05;letter-spacing:-.02em;text-wrap:balance;margin:0}
.wrap{width:100%;max-width:1200px;margin-inline:auto;padding-inline:clamp(16px,4.5vw,48px)}
.eyebrow{font-size:.7rem;font-weight:500;letter-spacing:.26em;text-transform:uppercase;color:var(--gold)}
.muted{color:var(--muted)}
:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.6em;font-weight:500;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;padding:1em 1.6em;border-radius:var(--r);border:1px solid transparent;text-decoration:none;cursor:pointer;min-height:48px;font-family:var(--font)}
.btn-gold{background:var(--gold);color:var(--on-gold)}
.btn-gold:hover{background:var(--gold-soft)}
.btn-line{background:transparent;color:var(--ink);border-color:color-mix(in srgb,var(--ink) 40%,transparent)}
.btn-line:hover{border-color:var(--gold);color:var(--gold)}
.btn-wa{background:var(--wa);color:#fff}
.btn svg{width:1.2em;height:1.2em}
.pend{display:inline-flex;font-size:.64rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;font-style:normal;color:var(--pend-ink);background:var(--pend-bg);border:1px dashed var(--pend-line);border-radius:3px;padding:.25em .55em;line-height:1.3}
.review{background:var(--pend-bg);color:var(--pend-ink);font-size:.8rem;border-bottom:1px dashed var(--pend-line)}
.review .wrap{display:flex;gap:.4rem 1rem;align-items:center;justify-content:space-between;flex-wrap:wrap;padding-block:.5rem}
.review button{font:inherit;font-weight:500;background:none;border:0;color:inherit;text-decoration:underline;cursor:pointer;padding:.3rem 0}
header.site{position:sticky;top:env(safe-area-inset-top,0px);z-index:40;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:.75rem}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none;min-width:0}
.brand .name{font-style:italic;font-weight:300;font-size:1.55rem;line-height:1;white-space:nowrap}
.brand .sub{font-size:.58rem;font-weight:500;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
nav.main{display:flex;gap:2rem;font-size:.78rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase}
nav.main a{text-decoration:none;color:var(--muted);padding-block:.3rem}
nav.main a:hover,nav.main a[aria-current]{color:var(--ink)}
.head-cta .btn{min-height:42px;padding:.75em 1.2em;font-size:.72rem}
@media (max-width:900px){nav.main{gap:1.1rem;font-size:.66rem;letter-spacing:.1em}nav.main .hide-m{display:none}.head-cta{display:none}}
@media (max-width:420px){.brand .sub{display:none}}
.dock{position:fixed;left:0;right:0;bottom:0;z-index:50;display:none;gap:.5rem;padding:.6rem 16px calc(.6rem + env(safe-area-inset-bottom,0px));background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(10px);border-top:1px solid var(--line)}
.dock .btn{flex:1;min-height:48px;padding:.8em;font-size:.72rem}
@media (max-width:900px){.dock{display:flex}footer .wrap{padding-bottom:calc(2.4rem + 76px)}}
footer{border-top:1px solid var(--line);font-size:.82rem;color:var(--muted);margin-top:clamp(3rem,8vw,5rem)}
footer .wrap{display:flex;flex-wrap:wrap;gap:1rem 2rem;justify-content:space-between;padding-block:2.4rem}
footer .name{font-style:italic;font-weight:300;font-size:1.6rem;color:var(--ink)}
.ph{position:relative;background:repeating-linear-gradient(135deg,var(--surface) 0 14px,var(--bg-2) 14px 28px);border-radius:var(--r);overflow:hidden;display:grid;place-items:center}
.ph .pend{position:absolute;top:.7rem;left:.7rem}
.ph span.ph-t{font-style:italic;font-weight:300;font-size:1.1rem;color:color-mix(in srgb,var(--ink) 55%,transparent);padding:1rem;text-align:center}

/* listado */
.intro{padding-block:clamp(2.5rem,7vw,5rem) clamp(1.5rem,4vw,2.5rem);display:grid;gap:1rem}
.intro h1{font-size:clamp(3rem,9vw,6rem)}
.intro .muted{max-width:56ch;font-size:1.08rem}
.filters{display:grid;gap:.7rem;padding-block:1.2rem;border-block:1px solid var(--line);margin-bottom:2rem}
.frow{display:flex;gap:.5rem;align-items:center;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.frow::-webkit-scrollbar{display:none}
.frow .lbl{flex:none;font-size:.62rem;font-weight:500;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);width:5.5rem}
.chip{flex:none;font:inherit;font-size:.82rem;padding:.5rem .95rem;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;min-height:40px}
.chip[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:var(--on-gold)}
.count{font-size:.8rem;color:var(--muted);margin-bottom:1rem}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(1rem,2.4vw,1.6rem)}
@media (max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.grid{grid-template-columns:1fr;gap:1rem}
  .rcard{grid-template-columns:120px minmax(0,1fr);grid-template-rows:auto auto 1fr;column-gap:1rem;row-gap:.3rem;align-items:start}
  .rcard .ph{grid-row:1/span 3;aspect-ratio:1}.rcard .ph .ph-t{display:none}.rcard .ph .pend{font-size:.56rem}
  .rcard h3{font-size:1.35rem}}
.rcard{display:grid;gap:.7rem;text-decoration:none;color:var(--ink);min-width:0}
.rcard .ph{aspect-ratio:4/3}
.rcard .meta{font-size:.7rem;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.rcard h3{font-size:1.65rem}
.rcard .small{font-size:.85rem;color:var(--muted)}
.rcard:hover h3{color:var(--gold-soft)}
.empty{padding:2rem 0;color:var(--muted)}

/* receta */
.crumbs{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);padding-top:clamp(1.5rem,4vw,2.5rem)}
.crumbs a{color:var(--gold);text-decoration:none}
.rhead{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(1.5rem,5vw,4rem);align-items:end;padding-block:1.2rem clamp(2rem,5vw,3rem)}
.rhead h1{font-size:clamp(2.6rem,7vw,5rem)}
.rhead .muted{font-size:1.1rem;margin-top:1rem;max-width:48ch}
.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-block:1px solid var(--line);margin:1.6rem 0 0}
.facts div{padding:.9rem 1rem .9rem 0;min-width:0}
.facts div+div{padding-left:1rem;border-left:1px solid var(--line)}
.facts dt{font-size:.62rem;font-weight:500;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
.facts dd{margin:.25rem 0 0;font-style:italic;font-weight:300;font-size:1.2rem;color:var(--gold);line-height:1.2}
.rhead .ph{aspect-ratio:4/5}
@media (max-width:860px){.rhead{grid-template-columns:1fr}.rhead .ph{aspect-ratio:4/3;order:-1}}
.body{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(2rem,5vw,4rem);align-items:start}
@media (max-width:860px){.body{grid-template-columns:1fr}}
.body h2{font-size:clamp(1.8rem,3.6vw,2.4rem);margin-bottom:1rem}
.ing{list-style:none;margin:0;padding:0}
.ing li{padding:.65rem 0;border-bottom:1px solid var(--line);font-size:1rem}
.made{margin-top:1.8rem;border:1px solid var(--gold);border-radius:var(--r);padding:1.1rem;display:grid;gap:.8rem}
.prod{display:flex;justify-content:space-between;align-items:center;gap:.8rem;flex-wrap:wrap;padding-top:.7rem;border-top:1px solid var(--line)}
.prod b{font-style:italic;font-weight:300;font-size:1.15rem;display:block;line-height:1.2}
.prod small{font-size:.75rem;color:var(--muted)}
.mini{font:inherit;font-size:.68rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;padding:.55rem .9rem;border-radius:var(--r);border:1px solid var(--line);background:transparent;color:var(--ink);text-decoration:none;min-height:40px;display:inline-flex;align-items:center}
.mini:hover{border-color:var(--gold);color:var(--gold)}
.steps{list-style:none;margin:0;padding:0;counter-reset:s}
.steps li{counter-increment:s;display:grid;grid-template-columns:2.6rem minmax(0,1fr);gap:.8rem;padding:1rem 0;border-bottom:1px solid var(--line)}
.steps li::before{content:counter(s);font-style:italic;font-weight:300;font-size:1.9rem;line-height:1;color:var(--gold)}
.tip{margin-top:1.8rem;background:var(--surface);border-radius:var(--r);padding:1.2rem 1.3rem;display:grid;gap:.4rem}
.tip p{font-style:italic;font-weight:300;font-size:1.25rem;line-height:1.4}
.biz{margin-top:clamp(3rem,7vw,4.5rem);background:var(--bg-2);border-block:1px solid var(--line);padding-block:clamp(2rem,5vw,3rem)}
.biz .wrap{display:grid;grid-template-columns:minmax(0,1.3fr) auto;gap:1.4rem 3rem;align-items:center}
.biz h2{font-size:clamp(1.8rem,3.6vw,2.4rem);margin-block:.6rem}
.biz p.muted{max-width:60ch}
@media (max-width:760px){.biz .wrap{grid-template-columns:1fr}}
.more{margin-top:clamp(3rem,7vw,4.5rem)}
.more h2{font-size:clamp(1.8rem,3.6vw,2.4rem);margin-bottom:1.4rem}
"""

WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.8-1.4a.5.5 0 0 0 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.4-.3Z"/></svg>'

JS_PEND = """
<script>
(function(){
  var hidden=false; try{hidden=localStorage.getItem('lv-hide-pend')==='1';}catch(e){}
  function apply(){document.querySelectorAll('[data-pend]').forEach(function(el){el.hidden=hidden;});var r=document.getElementById('review');if(r)r.hidden=hidden;}
  var b=document.getElementById('hideReview'); if(b) b.onclick=function(){hidden=true;try{localStorage.setItem('lv-hide-pend','1');}catch(e){}apply();};
  apply();
})();
</script>
"""


def pagina(titulo, descripcion, cuerpo, pre, actual="recetas", scripts=""):
    wa_gen = f"https://wa.me/{WA}?text=" + quote("Hola Los Valles, quiero información de sus productos.")
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="review" id="review"><div class="wrap">
  <span><b>Versión de revisión.</b> Recetas por probar y fotografiar en la cocina de Los Valles antes de publicarlas.</span>
  <button type="button" id="hideReview">Ocultar marcas</button>
</div></div>
<header class="site"><div class="wrap">
  <a class="brand" href="{pre}index.html" aria-label="Los Valles, inicio"><span class="name">Los Valles</span><span class="sub">Deshidratados</span></a>
  <nav class="main" aria-label="Principal">
    <a href="{pre}index.html#productos">Productos</a>
    <a class="hide-m" href="{pre}index.html#negocios">Para negocios</a>
    <a href="{pre}recetas.html"{' aria-current="page"' if actual == 'recetas' else ''}>Recetas</a>
    <a href="{pre}index.html#contacto">Contacto</a>
  </nav>
  <div class="head-cta"><a class="btn btn-gold" href="{pre}index.html#contacto">Cotiza para tu negocio</a></div>
</div></header>
<main>
{cuerpo}
</main>
<footer><div class="wrap">
  <div><div class="name">Los Valles</div><div>Productos deshidratados · Rionegro, Antioquia</div></div>
  <div style="display:grid;gap:.3rem"><span>+57 310 374 2028 · info@losvalles.com.co</span>
  <a href="https://www.instagram.com/losvalles_deshidratados/" target="_blank" rel="noopener">@losvalles_deshidratados</a></div>
</div></footer>
<div class="dock">
  <a class="btn btn-gold" href="{pre}index.html#contacto">Cotiza</a>
  <a class="btn btn-wa" href="{wa_gen}" target="_blank" rel="noopener">{WA_SVG}WhatsApp</a>
</div>
{JS_PEND}{scripts}
</body>
</html>
"""


def placeholder(texto):
    return f'<div class="ph"><span class="pend" data-pend>Foto pendiente</span><span class="ph-t">{e(texto)}</span></div>'


def tarjeta(r, pre):
    cats = sorted({categoria_producto(p["nombre"]) for p in r["productos"]})
    t = fmt_tiempo(r["tiempo"]) + (" " + r["tiempoExtra"] if r.get("tiempoExtra") else "")
    return (f'<a class="rcard" href="{pre}recetas/{r["slug"]}.html" data-grupo="{e(r["grupo"])}" '
            f'data-prod="{e("|".join(cats))}" data-tiempo="{rango_tiempo(r["tiempo"])}">'
            f'{placeholder(r["titulo"])}'
            f'<span class="meta">{e(r["sub"])} · {e(fmt_tiempo(r["tiempo"]))}</span>'
            f'<h3>{e(r["titulo"])}</h3>'
            f'<span class="small">{e(r["porciones"])} · {e(r["dificultad"])}{" · " + e(r["tiempoExtra"]) if r.get("tiempoExtra") else ""}</span></a>')


def listado():
    prods = ["Aromáticas", "Frutas", "Tomates", "4&CO", "Limón y naranja"]
    chips = lambda key, vals: "".join(
        f'<button class="chip" type="button" data-f="{key}" data-v="{e(v)}" aria-pressed="{"true" if v == "" else "false"}">{e(lbl)}</button>'
        for v, lbl in vals)
    cuerpo = f"""
<section class="wrap intro">
  <span class="eyebrow">Recetas</span>
  <h1>En la cocina.</h1>
  <p class="muted">Ideas para usar nuestros deshidratados en bebidas, desayunos, repostería y cocina salada. Cada receta indica qué productos usar y cómo adaptarla para tu negocio.</p>
</section>
<section class="wrap">
  <div class="filters" role="group" aria-label="Filtrar recetas">
    <div class="frow"><span class="lbl">Tipo</span>{chips("grupo", [("", "Todas")] + [(g, g) for g in GRUPOS])}</div>
    <div class="frow"><span class="lbl">Producto</span>{chips("prod", [("", "Todos")] + [(p, p) for p in prods])}</div>
    <div class="frow"><span class="lbl">Tiempo</span>{chips("tiempo", [("", "Cualquiera"), ("rapida", "Menos de 15 min"), ("media", "15 a 45 min"), ("larga", "Más de 45 min")])}</div>
  </div>
  <p class="count" id="count" aria-live="polite"></p>
  <div class="grid" id="grid">{"".join(tarjeta(r, "") for r in RECETAS)}</div>
  <p class="empty" id="empty" hidden>No hay recetas con esos filtros. Prueba quitando alguno.</p>
</section>
"""
    js = """
<script>
(function(){
  var f={grupo:'',prod:'',tiempo:''};
  var cards=[].slice.call(document.querySelectorAll('.rcard'));
  function run(){
    var n=0;
    cards.forEach(function(c){
      var ok=(!f.grupo||c.dataset.grupo===f.grupo)&&(!f.prod||c.dataset.prod.split('|').indexOf(f.prod)>-1)&&(!f.tiempo||c.dataset.tiempo===f.tiempo);
      c.hidden=!ok; if(ok)n++;
    });
    document.getElementById('count').textContent=n+(n===1?' receta':' recetas');
    document.getElementById('empty').hidden=n>0;
  }
  document.querySelectorAll('.chip').forEach(function(b){
    b.addEventListener('click',function(){
      f[b.dataset.f]=b.dataset.v;
      document.querySelectorAll('.chip[data-f="'+b.dataset.f+'"]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
      run();
    });
  });
  run();
})();
</script>
"""
    return pagina("Recetas · Los Valles Deshidratados",
                  "Recetas con frutas, aromáticas y tomates deshidratados de Los Valles: bebidas, desayunos, repostería y cocina salada.",
                  cuerpo, "", scripts=js)


def receta(r):
    pre = "../"
    t = fmt_tiempo(r["tiempo"]) + (f' <small style="font-size:.8rem;color:var(--muted)">{e(r["tiempoExtra"])}</small>' if r.get("tiempoExtra") else "")
    prods = []
    for p in r["productos"]:
        if p["tipo"] == "casa":
            msg = f'Hola Los Valles, quiero pedir: {p["nombre"]} ({p["detalle"]}). Lo vi en la receta "{r["titulo"]}".'
            accion = f'<a class="mini" href="https://wa.me/{WA}?text={quote(msg)}" target="_blank" rel="noopener">Pedir por WhatsApp</a>'
        else:
            accion = f'<a class="mini" href="{pre}index.html#contacto">Cotizar</a>'
        prods.append(f'<div class="prod"><span><b>{e(p["nombre"])}</b><small>{e(p["detalle"])}</small></span>{accion}</div>')
    otras = [x for x in RECETAS if x["grupo"] == r["grupo"] and x["slug"] != r["slug"]]
    otras += [x for x in RECETAS if x["grupo"] != r["grupo"]]
    cuerpo = f"""
<div class="wrap">
  <p class="crumbs"><a href="{pre}recetas.html">Recetas</a> / {e(r["grupo"])} / {e(r["sub"])}</p>
  <section class="rhead">
    <div>
      <h1>{e(r["titulo"])}</h1>
      <p class="muted">{e(r["intro"])}</p>
      <dl class="facts">
        <div><dt>Tiempo</dt><dd>{t}</dd></div>
        <div><dt>Rinde</dt><dd>{e(r["porciones"])}</dd></div>
        <div><dt>Dificultad</dt><dd>{e(r["dificultad"])}</dd></div>
      </dl>
    </div>
    {placeholder("Foto del plato terminado")}
  </section>
  <section class="body">
    <div>
      <h2>Ingredientes</h2>
      <ul class="ing">{"".join(f"<li>{e(i)}</li>" for i in r["ingredientes"])}</ul>
      <div class="made"><span class="eyebrow">Hecho con Los Valles</span>{"".join(prods)}</div>
    </div>
    <div>
      <h2>Preparación</h2>
      <ol class="steps">{"".join(f"<li><span>{e(s)}</span></li>" for s in r["pasos"])}</ol>
      <div class="tip"><span class="eyebrow">Tip de la casa</span><p>{e(r["tip"])}</p></div>
    </div>
  </section>
</div>
<section class="biz"><div class="wrap">
  <div><span class="eyebrow">Para tu negocio</span><h2>En tu carta.</h2><p class="muted">{e(r["negocio"])}</p></div>
  <a class="btn btn-gold" href="{pre}index.html#contacto">Cotiza para tu negocio</a>
</div></section>
<section class="wrap more">
  <h2>Más recetas</h2>
  <div class="grid">{"".join(tarjeta(x, pre) for x in otras[:3])}</div>
</section>
"""
    return pagina(f'{r["titulo"]} · Recetas Los Valles', r["intro"], cuerpo, pre)


def main():
    with open(os.path.join(RAIZ, "recetas.html"), "w", encoding="utf-8") as f:
        f.write(listado())
    os.makedirs(os.path.join(RAIZ, "recetas"), exist_ok=True)
    for r in RECETAS:
        with open(os.path.join(RAIZ, "recetas", r["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(receta(r))
    print(f"Generadas {len(RECETAS)} recetas + listado")


if __name__ == "__main__":
    main()
