const $ = (id) => document.getElementById(id);
let currentFile = null;
let currentProfile = null;
let currentColumns = [];
let toastTimer = null;

function toast(message, isError = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast show" + (isError ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.className = "toast", 3500);
}
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function fmt(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "number") return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined,{maximumFractionDigits:3});
  return String(value);
}
function selectedFile() { return currentFile; }
function updateFileLabel(file) {
  currentFile = file || null;
  $("fileSelected").textContent = file ? `${file.name} · ${(file.size/1024/1024).toFixed(2)} MB` : "No file selected";
  $("mlFileName").textContent = file ? file.name : "Choose a CSV above";
  $("sourceStatus").textContent = file ? "READY" : "WAITING";
}
$("fileInput").addEventListener("change", e => updateFileLabel(e.target.files[0]));
const dz = $("dropzone");
dz.addEventListener("dragover", e => { e.preventDefault(); dz.classList.add("dragover"); });
dz.addEventListener("dragleave", () => dz.classList.remove("dragover"));
dz.addEventListener("drop", e => {
  e.preventDefault(); dz.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.name.toLowerCase().endsWith(".csv")) {
    const dt = new DataTransfer(); dt.items.add(file); $("fileInput").files = dt.files; updateFileLabel(file);
  } else toast("Please drop a CSV file.", true);
});
function formDataWithFile(extra = {}) {
  if (!currentFile) throw new Error("Choose a CSV file or load the sample dataset first.");
  const fd = new FormData(); fd.append("file", currentFile);
  Object.entries(extra).forEach(([k,v]) => fd.append(k,v));
  return fd;
}
async function postJson(url, fd) {
  const res = await fetch(url, {method:"POST", body:fd});
  const data = await res.json();
  if (!res.ok || !data.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}
function renderKpis(p) {
  const items = [
    ["Total rows", fmt(p.rows), "Observations in dataset"],
    ["Total columns", fmt(p.columns), "Available features"],
    ["Missing cells", fmt(p.missing), `${p.missing_pct}% of all cells`],
    ["Duplicate rows", fmt(p.duplicates), `${p.numeric_columns} numeric · ${p.categorical_columns} categorical`]
  ];
  $("kpiGrid").innerHTML = items.map(([label,value,sub]) => `<div class="kpi-card"><span>${label}</span><b>${value}</b><small>${sub}</small></div>`).join("");
}
function renderTable(columns) {
  $("columnTable").innerHTML = columns.map(c => {
    const summary = c.mean !== undefined ? `μ ${fmt(c.mean)}` : (c.top_value ? `Top: ${esc(c.top_value)}` : "—");
    return `<tr><td>${esc(c.name)}</td><td>${esc(c.dtype)}</td><td>${fmt(c.missing)}</td><td>${fmt(c.unique)}</td><td>${summary}</td></tr>`;
  }).join("");
}
function renderPreview(rows) {
  if (!rows.length) { $("previewTable").innerHTML = "<p>No rows to preview.</p>"; return; }
  const cols = Object.keys(rows[0]);
  $("previewTable").innerHTML = `<table><thead><tr>${cols.map(c=>`<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${esc(fmt(r[c]))}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}
function renderDistribution(dfPreview, column, allSummary) {
  // Charts are generated from the uploaded data on the server in a compact preview.
  const rowValues = dfPreview.map(r => r[column]).filter(v => v !== null && v !== undefined);
  const isNumeric = rowValues.length && rowValues.every(v => typeof v === "number");
  let trace, layout;
  if (isNumeric) {
    trace = {x:rowValues,type:"histogram",marker:{color:"#8270f3"},opacity:.9};
    layout = {xaxis:{title:column,gridcolor:"#eeeeF5"},yaxis:{title:"Count",gridcolor:"#eeeeF5"},margin:{l:45,r:15,t:15,b:45},paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",font:{family:"DM Sans",size:10,color:"#85899d"}};
  } else {
    const counts = {};
    rowValues.forEach(v=>{const k=String(v);counts[k]=(counts[k]||0)+1;});
    const pairs = Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,12);
    trace = {x:pairs.map(x=>x[0]),y:pairs.map(x=>x[1]),type:"bar",marker:{color:"#8270f3"}};
    layout = {xaxis:{title:column,gridcolor:"#eeeeF5"},yaxis:{title:"Count",gridcolor:"#eeeeF5"},margin:{l:45,r:15,t:15,b:70},paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",font:{family:"DM Sans",size:10,color:"#85899d"}};
  }
  Plotly.newPlot("distributionChart",[trace],layout,{responsive:true,displayModeBar:false});
}
let lastPreview = [];
$("uploadForm").addEventListener("submit", async e => {
  e.preventDefault();
  if (!currentFile) return toast("Choose a CSV file first.", true);
  $("analyzeBtn").disabled = true; $("analyzeBtn").innerHTML = "Analyzing…";
  try {
    const data = await postJson("/api/analyze", formDataWithFile());
    currentProfile = data.profile; currentColumns = data.columns; lastPreview = data.preview;
    renderKpis(data.profile); renderTable(data.summary); renderPreview(data.preview);
    $("datasetTitle").textContent = currentFile.name;
    $("datasetSubtitle").textContent = `${fmt(data.profile.rows)} rows · ${fmt(data.profile.columns)} columns · ${data.profile.memory_kb} KB in memory`;
    $("targetSelect").innerHTML = data.columns.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join("");
    $("chartColumn").innerHTML = data.columns.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join("");
    $("results").classList.remove("hidden");
    $("reportHint").textContent = "Your dataset profile is ready to export.";
    renderDistribution(lastPreview, $("chartColumn").value, data.summary);
    $("results").scrollIntoView({behavior:"smooth",block:"start"});
    toast("Dataset analyzed successfully.");
  } catch(err) { toast(err.message, true); }
  finally { $("analyzeBtn").disabled = false; $("analyzeBtn").innerHTML = 'Analyze dataset <span>→</span>'; }
});
$("chartColumn").addEventListener("change",()=>renderDistribution(lastPreview,$("chartColumn").value,[]));
$("taskSelect").addEventListener("change", () => {
  const task = $("taskSelect").value;
  $("targetWrap").classList.toggle("hidden", !["classification","regression"].includes(task));
  $("clustersWrap").classList.toggle("hidden", task !== "clustering");
});
$("mlForm").addEventListener("submit", async e => {
  e.preventDefault();
  const task = $("taskSelect").value;
  const extra = {task};
  if (["classification","regression"].includes(task)) {
    if (!$("targetSelect").value) return toast("Analyze a dataset and select a target column first.", true);
    extra.target = $("targetSelect").value;
  }
  if (task === "clustering") extra.clusters = $("clustersSelect").value;
  $("runMlBtn").disabled = true; $("runMlBtn").textContent = "Running experiment…";
  try {
    const data = await postJson("/api/ml", formDataWithFile(extra));
    renderMlResult(data.result);
    $("mlOutput").scrollIntoView({behavior:"smooth",block:"center"});
    toast("Experiment completed.");
  } catch(err) { toast(err.message, true); }
  finally { $("runMlBtn").disabled = false; $("runMlBtn").innerHTML = 'Run experiment <span>→</span>'; }
});
function renderMlResult(r) {
  let metrics = [];
  if (r.metrics) metrics = Object.entries(r.metrics).map(([k,v])=>[k.replaceAll("_"," "),v === null ? "N/A" : (typeof v === "number" ? (v*1 === v && Math.abs(v) <= 1 ? (v*100).toFixed(1)+"%" : fmt(v)) : v)]);
  else if (r.task === "Clustering") metrics = [["Rows clustered",fmt(r.rows_clustered)],["Clusters",fmt(r.clusters)],["Silhouette score",r.silhouette_score ?? "N/A"]];
  else metrics = [["Rows analyzed",fmt(r.rows_analyzed)],["Anomalies detected",fmt(r.anomalies_detected)],["Anomaly rate",r.anomaly_percentage+"%"]];
  let extra = "";
  if (r.confusion_matrix) {
    extra = `<div class="result-chart"><h3>Confusion matrix</h3><div class="table-wrap"><table><thead><tr><th>Actual \\ Predicted</th>${r.labels.map(x=>`<th>${esc(x)}</th>`).join("")}</tr></thead><tbody>${r.confusion_matrix.map((row,i)=>`<tr><td>${esc(r.labels[i])}</td>${row.map(v=>`<td>${fmt(v)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>`;
  } else if (r.cluster_counts) {
    const max = Math.max(...r.cluster_counts.map(x=>x.count),1);
    extra = `<div class="cluster-list">${r.cluster_counts.map(c=>`<div class="cluster-row"><b>${esc(c.cluster)}</b><div class="cluster-bar"><span style="width:${c.count/max*100}%"></span></div><span>${fmt(c.count)}</span></div>`).join("")}</div>`;
  } else if (r.preview) {
    const cols = Object.keys(r.preview[0]||{}).slice(-2);
    extra = `<div class="result-chart"><h3>Sample anomaly results</h3><div class="table-wrap"><table><thead><tr>${cols.map(c=>`<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${r.preview.slice(0,8).map(row=>`<tr>${cols.map(c=>`<td>${esc(fmt(row[c]))}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>`;
  }
  $("mlOutput").innerHTML = `<div class="ml-result"><div class="ml-result-head"><div><div class="eyebrow muted">${esc(r.task.toUpperCase())} · RESULTS</div><h3>${esc(r.algorithm)}</h3><p class="panel-intro">${r.target ? "Target: "+esc(r.target)+" · " : ""}${r.train_rows ? `${fmt(r.train_rows)} train / ${fmt(r.test_rows)} test rows` : ""}</p></div><span class="model-tag">EXPERIMENT COMPLETE</span></div><div class="metric-grid">${metrics.map(([k,v])=>`<div class="metric"><small>${esc(k)}</small><b>${esc(String(v))}</b></div>`).join("")}</div>${extra}<div class="result-note">ⓘ ${esc(r.note || "Review results in the context of your dataset before making decisions.")}</div></div>`;
}
$("loadSample").addEventListener("click", () => {
  const csv = "customer_age,monthly_spend,visits_per_month,plan,churn\n22,19,2,Basic,Yes\n35,45,8,Premium,No\n29,24,3,Basic,Yes\n46,68,12,Premium,No\n31,39,7,Standard,No\n24,21,2,Basic,Yes\n52,75,14,Premium,No\n41,55,10,Standard,No\n27,28,4,Basic,Yes\n38,48,8,Standard,No\n33,35,6,Standard,No\n23,18,1,Basic,Yes\n49,71,13,Premium,No\n30,27,3,Basic,Yes\n44,61,11,Premium,No\n26,25,3,Basic,Yes\n36,42,7,Standard,No\n55,79,15,Premium,No\n28,31,5,Standard,Yes\n40,52,9,Standard,No\n";
  currentFile = new File([csv], "sample_customer_churn.csv", {type:"text/csv"});
  updateFileLabel(currentFile);
  $("fileSelected").textContent = "Sample dataset loaded · illustrative data";
  toast("Sample dataset loaded. Click Analyze dataset to begin.");
});
$("downloadReport").addEventListener("click", async () => {
  if (!currentFile) return toast("Choose a CSV or load the sample dataset first.", true);
  const btn = $("downloadReport"); btn.disabled = true;
  try {
    const res = await fetch("/api/report",{method:"POST",body:formDataWithFile()});
    if (!res.ok) { const err=await res.json(); throw new Error(err.error||"Could not generate report."); }
    const blob = await res.blob(); const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href=url; a.download="datalab-analysis-report.txt"; a.click(); URL.revokeObjectURL(url);
    toast("Report downloaded.");
  } catch(err) { toast(err.message,true); }
  finally { btn.disabled = false; }
});
$("themeToggle").addEventListener("click",()=>document.body.classList.toggle("dark"));
document.querySelectorAll(".nav-link").forEach(link=>link.addEventListener("click",()=>{
  document.querySelectorAll(".nav-link").forEach(x=>x.classList.remove("active"));link.classList.add("active");
}));
