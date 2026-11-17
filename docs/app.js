const $=id=>document.getElementById(id);
const names={baseline:'Mean baseline',ridge:'Ridge',forest:'Random Forest'};
const fmt=x=>Number(x).toFixed(3);
let rows=[],summary;
function options(id,values){const el=$(id),old=el.value;el.replaceChildren(...values.map(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;return o}));if(values.map(String).includes(old))el.value=old;}
function unique(data,key){return [...new Set(data.map(r=>r[key]))].sort((a,b)=>a-b)}
function cells(values){const tr=document.createElement('tr');for(const v of values){const td=document.createElement('td');td.textContent=v;tr.append(td)}return tr}
function filtered(keys){return rows.filter(r=>keys.every(k=>String(r[k])===$({shape_id:'shape',orientation:'orientation',glazing_area:'glazing',glazing_distribution:'distribution'}[k]).value))}
function updateFilters(level){if(level<=0)options('orientation',unique(filtered(['shape_id']),'orientation'));if(level<=1)options('glazing',unique(filtered(['shape_id','orientation']),'glazing_area'));if(level<=2)options('distribution',unique(filtered(['shape_id','orientation','glazing_area']),'glazing_distribution'));render()}
function render(){const target=$('target').value,model=$('model').value,r=filtered(['shape_id','orientation','glazing_area','glazing_distribution'])[0];if(!r)return;
const actual=r[target],pred=r[`${target}_${model}`],error=pred-actual;
$('cards').replaceChildren(...[['Simulated load',actual],['Predicted load',pred],['Absolute error',Math.abs(error)]].map(([label,value])=>{const d=document.createElement('div');d.className='card';const s=document.createElement('span');s.textContent=label;const b=document.createElement('strong');b.textContent=fmt(value);d.append(s,b);return d}));
$('configuration').textContent=`Row ${r.row_id} · compactness ${r.relative_compactness} · surface ${r.surface_area} · wall ${r.wall_area} · roof ${r.roof_area} · height ${r.overall_height}. Signed error: ${fmt(error)} dataset units.`;
const max=Math.max(actual,pred,1)*1.15;
$('bars').innerHTML=`<text x="18" y="44" fill="#294768">Simulated</text><rect x="125" y="20" height="36" width="${Math.max(0,actual)/max*490}" fill="#5289e9"/><text x="18" y="110" fill="#294768">Predicted</text><rect x="125" y="86" height="36" width="${Math.max(0,pred)/max*490}" fill="#8ca5c8"/><text x="125" y="148" fill="#294768">Dataset units · same scale for both bars</text>`;
const worst=[...rows].sort((a,b)=>Math.abs(b[target]-b[`${target}_${model}`])-Math.abs(a[target]-a[`${target}_${model}`])).slice(0,5);
$('worst').replaceChildren(...worst.map(v=>cells([v.row_id,v.shape_id,fmt(v[target]),fmt(v[`${target}_${model}`]),fmt(Math.abs(v[target]-v[`${target}_${model}`]))])));
const w=worst[0];$('error-note').textContent=`For ${names[model]} and ${target.replaceAll('_',' ')}, the largest held-out absolute error is ${fmt(Math.abs(w[target]-w[`${target}_${model}`]))} on row ${w.row_id}, shape ${w.shape_id}, orientation ${w.orientation}, glazing area ${w.glazing_area}, distribution ${w.glazing_distribution}. Compare this configuration with the per-shape table; this observation alone does not establish why the error occurred.`;
}
async function load(){try{const responses=await Promise.all(['summary','predictions'].map(n=>fetch(`data/${n}.json`)));if(responses.some(r=>!r.ok))throw Error('Missing result files');[summary,rows]=await Promise.all(responses.map(r=>r.json()));
$('status').textContent=`Loaded ${rows.length} held-out configurations. All displayed scores come from the saved Python run.`;
$('audit').textContent=`Verified: ${summary.audit.rows} rows, ${summary.audit.features} inputs, ${summary.audit.duplicate_source_rows} duplicate source rows, zero missing values. ${summary.audit.empty_spreadsheet_rows_removed} completely empty spreadsheet rows removed.`;
$('split').textContent=`Saved split: ${summary.development_rows} development configurations from shapes ${summary.development_shapes.join(', ')}; ${summary.test_rows} test configurations from shapes ${summary.test_shapes.join(', ')}. Shape IDs are arbitrary geometry identifiers.`;
$('metrics').replaceChildren(...summary.metrics.map(m=>{const vals=summary.cv.filter(v=>v.target===m.target&&v.model===m.model).map(v=>v.mae);const mean=vals.reduce((a,b)=>a+b,0)/vals.length;const sd=Math.sqrt(vals.reduce((a,b)=>a+(b-mean)**2,0)/(vals.length-1));return cells([m.target.replaceAll('_',' '),names[m.model],fmt(m.mae),fmt(m.rmse),`${fmt(mean)} ± ${fmt(sd)}`])}));
const findings=['heating_load','cooling_load'].map(t=>{const ms=summary.metrics.filter(m=>m.target===t);const best=ms.reduce((a,b)=>a.mae<b.mae?a:b),base=ms.find(m=>m.model==='baseline');return `${t.replaceAll('_',' ')}: ${names[best.model]} has the lowest observed test MAE (${fmt(best.mae)}), compared with ${fmt(base.mae)} for the baseline.`});
// Narrative conclusions are rendered from the same saved results by build_report.py.
$('shape-errors').replaceChildren(...summary.per_shape.map(m=>cells([m.target.replaceAll('_',' '),names[m.model],m.shape_id,fmt(m.mae)])));
options('shape',unique(rows,'shape_id'));updateFilters(0);
$('shape').onchange=()=>updateFilters(0);$('orientation').onchange=()=>updateFilters(1);$('glazing').onchange=()=>updateFilters(2);for(const id of ['distribution','target','model'])$(id).onchange=render;
}catch(e){$('status').textContent='Could not load results. Run python src/train.py, then serve docs using python -m http.server 8000 --directory docs. '+e.message;}}
load();
