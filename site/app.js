const PRODUCTS = {celulares: "Celulares", smartband: "Smartband", tv: "TV"};
const $ = (s, el = document) => el.querySelector(s);
const cache = {};
async function loadProduct(p) { return cache[p] ??= await (await fetch(`data/${p}.json`)).json(); }

function fmt(v) {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : String(Math.round(v * 100) / 100);
  return String(v);
}
function tableHTML(cols, rows, idx) {
  const head = (idx ? "<th></th>" : "") + cols.map(c => `<th>${esc(c)}</th>`).join("");
  const body = rows.map((r, i) => "<tr>" + (idx ? `<th>${esc(idx[i])}</th>` : "") + r.map(v => `<td>${esc(fmt(v))}</td>`).join("") + "</tr>").join("");
  return `<div class="tablewrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
function tbl(t) { return tableHTML(t.columns, t.rows, t.index); }
function fillProductSelect(sel) {
  sel.innerHTML = '<option value="">—</option>' + Object.entries(PRODUCTS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
}

/* ---------- Evaluador de alternativas ---------- */
const CATS = ["No es importante", "Poco importante", "Algo importante", "Importante", "Muy importante"];
const HELP_PRECIO = "Precio y marca del dispositivo. Aclaración: generalmente, a mayor importancia, se buscarán precios más bajos aunque siempre se priorizará una mayor relación precio-calidad";
const HELP_BAT = "Tiempo de duración de la batería";
const HELP_TAM = "Tamaño de pantalla del dispositivo. Aclaración: generalmente, a mayor importancia, se priorizarán tamaños de pantalla más grandes";
const HELP_DIS = "Estética, calidad de materiales y resistencia a caídas, a agua y a polvo";
const HELP_VEL = "Velocidad de procesamiento del dispositivo";
const HELP = {
  celulares: {precio: HELP_PRECIO, bateria: HELP_BAT, camara: "Resoluciones de foto y video tanto de la cámara frontal como de la cámara trasera", diseño: HELP_DIS,
    funciones: "Cantidad y calidad de funciones adicionales del dispositivo (por ejemplo, NFC, resistencia al agua, lector de huella, entre otros)",
    memoria: "Capacidad de almacenamiento interno. En otras palabras, espacio para descargar muchas aplicaciones, guardar muchas fotos o documentos, etcétera",
    pantalla: "Calidad de imagen de la pantalla", señal: "Calidad y estabilidad de la conectividad (datos móviles, wifi, entre otros)",
    sonido: "Calidad del sonido, cantidad de parlantes y ubicación de los mismos", tamaño: HELP_TAM, velocidad: HELP_VEL},
  tv: {control: "Sencillez y calidad del control remoto (facilidad de uso, teclado numérico en control, integrado con comando por voz, etcétera)",
    conexion: "Estabilidad en las distintas conexiones (internet, ethernet y bluetooth) y cantidad de entradas/puertos", diseño: "Estética y calidad de materiales",
    imagen: "Calidad de imagen de la pantalla", precio: HELP_PRECIO,
    sistema: "Facilidad de uso del dispositivo y cantidad y calidad de aplicaciones que trae o que se pueden instalar (por ejemplo, netflix, youtube, disney+, spotify, etcétera)",
    sonido: "Calidad de sonido y cantidad de parlantes", tamaño: HELP_TAM, velocidad: HELP_VEL},
  smartband: {bluetooth: "Alcance del bluetooth y sincronización de datos con celular", bateria: HELP_BAT, diseño: HELP_DIS,
    funciones: "Cantidad y calidad de funciones (cuenta pasos, estres, etcétera)", pantalla: "Calidad de imagen de la pantalla y tamaño de ésta", precio: HELP_PRECIO},
};
const USOS = {celulares: {
  "Para jugar": {precio: 3, bateria: 4, camara: 2, pantalla: 4, memoria: 3, tamaño: 3, velocidad: 5, sonido: 3, diseño: 1, funciones: 2, señal: 3},
  "Para trabajar": {precio: 5, bateria: 4, camara: 3, pantalla: 3, memoria: 4, tamaño: 2, velocidad: 5, sonido: 2, diseño: 3, funciones: 3, señal: 5},
  "Para redes sociales": {precio: 3, bateria: 4, camara: 5, pantalla: 3, memoria: 3, tamaño: 3, velocidad: 4, sonido: 2, diseño: 3, funciones: 3, señal: 4},
  "Para comunicación": {precio: 5, bateria: 1, camara: 2, pantalla: 2, memoria: 1, tamaño: 4, velocidad: 1, sonido: 4, diseño: 2, funciones: 2, señal: 5},
}};

function initAlternativas() {
  const sel = $("#product"), box = $("#weights"), out = $("#results");
  fillProductSelect(sel);
  sel.onchange = async () => {
    out.innerHTML = ""; box.innerHTML = "";
    if (!sel.value) return;
    const p = sel.value, d = await loadProduct(p);
    const usos = USOS[p];
    let html = "<h3>Paso 2 de 3: asigná la importancia de cada característica</h3><p>Por cada característica elegí qué importancia tiene para vos y después tocá «Procesar».</p>";
    if (usos) html += `<p><label>¿Necesitás ayuda? Orientación según uso: <select id="uso"><option value="">Reestablecer</option>${Object.keys(usos).map(u => `<option>${u}</option>`).join("")}</select></label></p>`;
    html += d.needs.keys.map((k, i) => `<div class="need"><label for="w${i}">${i + 1}) ${esc(d.needs.labels[i].toUpperCase())} — <span class="val" id="v${i}"></span></label>
      <small>${esc(HELP[p][k] || "")}</small><input type="range" id="w${i}" data-key="${esc(k)}" min="1" max="5" step="1" value="3"></div>`).join("");
    html += '<button class="primary" id="go">Procesar</button>';
    box.innerHTML = html;
    const upd = () => d.needs.keys.forEach((_, i) => $(`#v${i}`).textContent = CATS[$(`#w${i}`).value - 1]);
    box.querySelectorAll("input[type=range]").forEach(r => r.oninput = upd);
    if (usos) $("#uso").onchange = e => {
      box.querySelectorAll("input[type=range]").forEach(r => r.value = e.target.value ? usos[e.target.value][r.dataset.key] : 3); upd();
    };
    upd();
    $("#go").onclick = () => results(d, [...box.querySelectorAll("input[type=range]")].map(r => +r.value), out);
  };
}

function results(d, pesos, out) {
  const rel = d.relation, techImp = rel.columns.map((_, j) => pesos.reduce((s, w, i) => s + w * rel.rows[i][j], 0));
  const impOf = Object.fromEntries(rel.columns.map((c, j) => [c, techImp[j]]));
  const vals = d.sent.map(row => row.reduce((s, sent, k) => sent === null ? s : s + sent * (impOf[d.attrs[k]] ?? 0), 0));
  const max = Math.max(...vals);
  const cols = [...d.display.columns, "porcentaje_recomendacion"];
  const rows = d.display.rows.map((r, i) => [...r, Math.round(vals[i] / max * 1000) / 10]);
  const order = rows.map((_, i) => i).sort((a, b) => rows[b][rows[b].length - 1] - rows[a][rows[a].length - 1] || a - b);
  const sorted = order.map(i => rows[i]), idx = sorted.map((_, i) => i + 1);
  out.innerHTML = `<h3>Paso 3 de 3: elegí tu alternativa</h3><p>Estas son las 10 alternativas que mejor se ajustan a lo que buscás. Analizamos todas las alternativas.</p>
    <h4>Las 10 alternativas que más te recomendamos</h4>${tableHTML(cols, sorted.slice(0, 10), idx)}
    <p class="muted"><em>Fecha de la última actualización de los datos: 29 de Junio de 2022</em></p>
    <details><summary>Ver todas las alternativas tenidas en cuenta en el análisis</summary>${tableHTML(cols, sorted, idx)}</details>`;
  out.scrollIntoView({behavior: "smooth"});
}

/* ---------- Evaluador de marcas ---------- */
function initMarcas() {
  const sel = $("#product"), out = $("#results");
  fillProductSelect(sel);
  sel.onchange = async () => {
    out.innerHTML = ""; if (!sel.value) return;
    const p = sel.value, c = (await loadProduct(p)).clusters;
    out.innerHTML = `<h3>Paso 2: conocé cada grupo de alternativas del producto</h3>
      <p>Según la similitud entre las alternativas en sus características, se las agrupó en distintos grupos.</p>
      <h4>Cantidad de grupos y sus nombres</h4>
      <ul><li>Nº grupos: ${c.perCluster.rows.length}</li><li>Nombres de grupos: ${c.perCluster.index.map(esc).join(" – ")}</li></ul>
      <h4>Cantidad de alternativas por grupo</h4><img src="img/cant_alt_${p}.png" alt="Cantidad de alternativas por grupo">
      <h4>Alternativa típica por grupo</h4><p>¿Cómo es la alternativa típica de cada grupo?</p>${tbl(c.centroids)}
      <h4>Posición de cada grupo en las necesidades del cliente</h4><p>Qué grupo cumple mejor con cada necesidad del cliente.</p>${tbl(c.best)}
      <h3>Paso 3: mirá con qué grupo se identifica más cada marca</h3>
      <div class="tabs"><button class="on" data-t="t">Tabla</button><button data-t="g">Gráfico</button></div>
      <div id="t">${tbl(c.brands)}</div>
      <div id="g" class="hidden"><img src="img/brand_${p}.png" alt="Marcas por grupo">
        <details><summary>Ayuda en interpretación del gráfico</summary><ul>
        <li>Más verde → mejor relación precio-calidad</li><li>Más amarillo/naranja → relación precio-calidad media</li><li>Más rojo → peor relación precio-calidad</li></ul></details></div>
      <details><summary>Ver todas las alternativas tenidas en cuenta en el análisis</summary>${tbl(c.alts)}</details>`;
    out.querySelectorAll(".tabs button").forEach(b => b.onclick = () => {
      out.querySelectorAll(".tabs button").forEach(x => x.classList.toggle("on", x === b));
      $("#t").classList.toggle("hidden", b.dataset.t !== "t"); $("#g").classList.toggle("hidden", b.dataset.t !== "g");
    });
  };
}
