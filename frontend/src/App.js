// ================================
// FILE: /app/frontend/src/App.js
// Single-file React app (Recharts + Tailwind). Use `export default App;` only.
// ================================
import React, { useEffect, useMemo, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from "recharts";

function useData(url){
  const [data,setData] = useState(null);
  const [error,setError] = useState(null);
  const [loading,setLoading] = useState(true);
  useEffect(()=>{ let alive = true; setLoading(true);
    fetch(url).then(r=>r.json()).then(d=>{ if(alive){ setData(d); setLoading(false);} })
    .catch(e=>{ if(alive){ setError(String(e)); setLoading(false);} });
    return ()=>{ alive=false };
  },[url]);
  return { data, error, loading };
}

function Banner({ errors }){
  if(!errors.length) return null;
  return (
    <div className="sticky top-0 z-20 bg-red-50 border-b border-red-200 text-red-800 text-sm px-4 py-2">{errors.join(" · ")}</div>
  );
}

function Skeleton({ className="h-6 w-24" }){
  return <div className={`animate-pulse bg-gray-100 rounded ${className}`} />
}

function HeroTile({ title, value, sub, footnoteId, onOpen, loading }){
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-gray-600">{title}</div>
          <div className="kpi">{loading ? <Skeleton className="h-7 w-20"/> : value}</div>
          <div className="kpi-sub">{loading ? <Skeleton className="h-3 w-28"/> : sub}</div>
        </div>
        {footnoteId && (
          <button className="badge" aria-label={`Open footnote ${footnoteId}`} onClick={()=>onOpen(footnoteId)}>FN {footnoteId}</button>
        )}
      </div>
    </div>
  );
}

function RatesChart({ data, loading, range, onRangeChange }){
  // Process data based on whether it's historical or current
  const chartData = data ? (
    Array.isArray(data) ? data.map(d => ({
      date: d.date,
      name: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      t5: d.t5,
      t10: d.t10, 
      t30: d.t30,
      ffr: d.ffr
    })) : 
    // Fallback to old format for current rates
    ["Jan","Feb","Mar","Apr","May","Jun"].map((name)=>({ 
      name, 
      t5: data.t5 ?? 4.5, 
      t10: data.t10 ?? 4.49, 
      t30: data.t30 ?? 4.66,
      ffr: data.ffr ?? 5.33
    }))
  ) : [];

  return (
    <div className="card h-80">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-gray-600">Treasury yields & Fed Funds, %</div>
        <div className="flex items-center gap-1">
          {["6M", "1Y", "Max"].map(r => (
            <button 
              key={r}
              className={`px-2 py-1 text-xs rounded ${range === r ? "bg-gray-900 text-white" : "bg-gray-100 hover:bg-gray-200"}`}
              onClick={() => onRangeChange(r)}
            >
              {r}
            </button>
          ))}
        </div>
      </div>
      {loading ? <Skeleton className="h-56 w-full"/> : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
            <XAxis 
              dataKey="name" 
              fontSize={10}
              tick={{ fontSize: 10 }}
              interval={Math.max(1, Math.floor(chartData.length / 8))} // Show ~8 labels max
            />
            <YAxis 
              domain={['dataMin - 0.1', 'dataMax + 0.1']} 
              fontSize={10}
              tick={{ fontSize: 10 }}
              tickFormatter={(value) => `${value.toFixed(1)}%`}
            />
            <Tooltip 
              formatter={(value, name) => [`${value?.toFixed(2)}%`, name]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend fontSize={10} />
            <Line type="monotone" dataKey="ffr" name="Fed Funds" stroke="#dc2626" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="t5" name="5y Treasury" stroke="#2563eb" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="t10" name="10y Treasury" stroke="#059669" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="t30" name="30y Treasury" stroke="#7c3aed" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function MaturityBar({ rows, loading }){
  return (
    <div className="card h-72">
      <div className="mb-2 text-sm text-gray-600">CRE maturities by asset type, % of total</div>
      {loading ? <Skeleton className="h-48 w-full"/> : (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows||[]} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
            <XAxis dataKey="year" fontSize={12} />
            <YAxis domain={[0, 100]} fontSize={12} />
            <Tooltip />
            <Legend />
            <Bar dataKey="mf" stackId="a" name="Multifamily" />
            <Bar dataKey="off" stackId="a" name="Office" />
            <Bar dataKey="ind" stackId="a" name="Industrial" />
            <Bar dataKey="other" stackId="a" name="Other" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function Drawer({ openId, onClose, register }){
  const text = openId ? register?.[openId] : null;
  return (
    <div className={`fixed inset-y-0 right-0 w-[28rem] bg-white border-l shadow-xl transition-transform ${openId?"translate-x-0":"translate-x-full"}`}>
      <div className="p-4 flex items-center justify-between border-b">
        <div className="text-sm font-semibold">Footnote {openId||""}</div>
        <button className="btn" onClick={onClose}>Close</button>
      </div>
      <div className="p-4 text-sm whitespace-pre-wrap">{text || "No footnote selected."}</div>
    </div>
  );
}

function BanksTab({ onOpen }){
  const [region, setRegion] = useState("");
  const banks = useData(`/api/banks${region?`?region=${encodeURIComponent(region)}`:``}`);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  useEffect(()=>{ if(selected){ fetch(`/api/banks/${selected.id}`).then(r=>r.json()).then(setDetail); }},[selected]);
  return (
    <div className="space-y-4">
      <div className="card">
        <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
          <div>Banks — CRE exposure leaderboard</div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-1">
              <span>Region</span>
              <select className="border rounded px-2 py-1 text-sm" value={region} onChange={e=>setRegion(e.target.value)}>
                <option value="">All</option>
                <option>West</option>
                <option>South</option>
                <option>Midwest</option>
              </select>
            </label>
          </div>
        </div>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-gray-500"><tr><th className="py-2">Bank</th><th>Type</th><th>Region</th><th className="text-right">CRE Share %</th><th></th></tr></thead>
            <tbody>
              {(banks.data?.rows||[]).map(b=> (
                <tr key={b.id} className="border-t">
                  <td className="py-2">{b.name}</td>
                  <td>{b.type}</td>
                  <td>{b.region}</td>
                  <td className="text-right">{b.creShare.toFixed(1)}</td>
                  <td className="text-right"><button className="badge" onClick={()=>setSelected(b)}>view</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pt-2 text-[11px] text-gray-500">FN <button className="underline" onClick={()=>onOpen('B1')}>B1</button></div>
      </div>
      {detail && (
        <div className="card">
          <div className="font-medium text-sm mb-2">{detail.name} — Exposure Mix</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(detail.exposure||{}).map(([k,v])=> (
              <div key={k} className="flex items-center justify-between"><span>{k.toUpperCase()}</span><span>{v}%</span></div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function WaterfallTab(){
  const [terms, setTerms] = useState({ mgmtFee: 0.02, pref: 0.08, splitLP: 0.6, splitGP: 0.4, grossIRR: 0.18 });
  const [result, setResult] = useState(null);
  const run = async () => {
    const r = await fetch('/api/waterfall/calc', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ terms }) });
    const d = await r.json(); setResult(d);
  };
  return (
    <div className="card">
      <div className="grid md:grid-cols-5 gap-3">
        {Object.entries(terms).map(([k,v])=> (
          <label key={k} className="text-sm">
            <div className="text-gray-600 mb-1">{k}</div>
            <input className="w-full border rounded-lg px-2 py-1" type="number" step="0.01" value={v} onChange={e=>setTerms({...terms, [k]: parseFloat(e.target.value)})} />
          </label>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-2">
        <button className="btn" onClick={run}>Calculate</button>
        {result && <div className="text-sm text-gray-600">Computed IRR {result.outputs.computedIRR}% | LP Net {result.outputs.lpNetIRR}% | GP Carry {result.outputs.gpCarry}%</div>}
      </div>
      {result && (
        <div className="mt-3 text-[11px] text-gray-500">Note: {result.note}</div>
      )}
    </div>
  );
}

function App(){
  const [view, setView] = useState("LP");
  const [active, setActive] = useState("Overview");
  const [openFn, setOpenFn] = useState(null);
  const [token, setToken] = useState(null);
  const [ratesRange, setRatesRange] = useState("6M");

  const rates = useData(`/api/rates?audience=${encodeURIComponent(view)}`);
  const maturities = useData(`/api/maturities?audience=${encodeURIComponent(view)}`);
  const footnotes = useData("/api/footnotes");
  
  // Historical rates data based on selected range
  const rangeDays = ratesRange === "6M" ? 180 : ratesRange === "1Y" ? 365 : 1095; // Max = 3 years
  const ratesHistory = useData(`/api/rates/history?days=${rangeDays}&audience=${encodeURIComponent(view)}`);

  const errors = [];
  if(rates.error) errors.push("Rates failed");
  if(maturities.error) errors.push("Maturities failed");
  if(footnotes.error) errors.push("Footnotes failed");

  // Use historical data for charts, fallback to current rates for overview tiles
  const chartData = ratesHistory.data?.data || [];
  const overviewData = useMemo(() => {
    if (chartData.length > 0) {
      // Use last few points from historical data for overview sparkline
      return chartData.slice(-6);
    }
    // Fallback to mock data
    const t5 = rates.data?.t5 ?? 4.5; 
    const t10 = rates.data?.t10 ?? 4.49; 
    const t30 = rates.data?.t30 ?? 4.66;
    const ffr = rates.data?.ffr ?? 5.33;
    return ["Jan","Feb","Mar","Apr","May","Jun"].map((name)=>({ name, t5, t10, t30, ffr }));
  }, [chartData, rates.data]);

  const tabs = ["Overview","Rates","CRE Maturities","Banks","Waterfall"];

  const footnoteRegister = (footnotes.data||[]).reduce((acc,fn)=>{acc[fn.id]=`${fn.label} | ${fn.source} | ${fn.retrievedAt || fn.lastUpdated} | ${fn.refresh} | ${fn.transform}`; return acc;}, {});

  return (
    <div className="min-h-screen">
      <Banner errors={errors} />
      {/* Header */}
      <div className="sticky top-0 z-10 border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="font-semibold">Coastal Oak — Living Pitch Deck</div>
            <span className="badge">{view}</span>
          </div>
          <div className="flex items-center gap-2">
            <button className={`tab ${view==="LP"?"tab-active":""}`} onClick={()=>setView("LP")}>LP</button>
            <button className={`tab ${view==="GP"?"tab-active":""}`} onClick={()=>setView("GP")}>GP</button>
            <button className={`tab ${view==="Internal"?"tab-active":""}`} onClick={()=>setView("Internal")}>Internal</button>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-12 gap-4">
        {/* Left TOC */}
        <div className="col-span-12 md:col-span-2 space-y-2">
          { tabs.map(tab => (
            <button key={tab} className={`w-full text-left tab ${active===tab?"tab-active":""}`} onClick={()=>setActive(tab)}>{tab}</button>
          )) }
          <div className="text-[11px] text-gray-500 pt-1">X-Coastal-Version: <code>{rates.error?"error":(rates.data?"live":"…")}</code></div>
        </div>

        {/* Center Canvas */}
        <div className="col-span-12 md:col-span-7 space-y-4">
          {active === "Overview" && (
            <>
              <div className="grid grid-auto gap-4">
                <HeroTile loading={rates.loading} title="Fed funds" value={`${(rates.data?.ffr??5.33).toFixed(2)}%`} sub={`As of ${rates.data?.ffr_date||"—"}`} footnoteId="F1" onOpen={setOpenFn} />
                <HeroTile loading={rates.loading} title="10y UST" value={`${(rates.data?.t10??4.49).toFixed(2)}%`} sub={`As of ${rates.data?.asOf||"—"}`} footnoteId="T1" onOpen={setOpenFn} />
                <HeroTile loading={maturities.loading} title="CRE maturities (this year)" value={`Mix view`} sub={`Breakdown below`} footnoteId="M1" onOpen={setOpenFn} />
              </div>
              <RatesChart loading={rates.loading} series={series} />
              <MaturityBar loading={maturities.loading} rows={maturities.data?.rows || []} />
            </>
          )}

          {active === "Rates" && <RatesChart loading={rates.loading} series={series} />}
          {active === "CRE Maturities" && <MaturityBar loading={maturities.loading} rows={maturities.data?.rows || []} />}
          {active === "Banks" && <BanksTab onOpen={setOpenFn} />}
          {active === "Waterfall" && <WaterfallTab />}
        </div>

        {/* Right Organizer */}
        <div className="col-span-12 md:col-span-3 space-y-4">
          <div className="card">
            <div className="mb-2 flex items-center justify-between">
              <div className="font-medium text-sm">Downloads</div>
            </div>
            <div className="space-y-2">
              <button className="btn w-full" onClick={async()=>{
                const r = await fetch('/api/deck/request', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ email: 'lp@example.com' }) });
                const d = await r.json(); setToken(d.token);
                alert(`Token issued: ${d.token}
Watermark: ${d.watermark}`);
              }}>Request Full Deck Access</button>
              <button disabled={!token} className="btn w-full disabled:opacity-50" onClick={async()=>{
                if(!token) return; const r = await fetch(`/api/deck/download?token=${encodeURIComponent(token)}`);
                const ok = r.ok; const d = await r.json().catch(()=>({}));
                alert(ok?`Download OK (stub)
${JSON.stringify(d)}`:`Denied: ${JSON.stringify(d)}`);
              }}>Download Deck (uses token)</button>
              
              {/* Executive Summary Downloads */}
              <div className="border-t pt-2 mt-3">
                <div className="text-xs text-gray-500 mb-2">Executive Summary</div>
                <a 
                  className="btn w-full" 
                  href={`/api/execsum/html?email=${encodeURIComponent('lp@example.com')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >Executive Summary (HTML)</a>
                <a 
                  className="btn w-full" 
                  href={`/api/execsum.pdf?email=${encodeURIComponent('lp@example.com')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  title="Watermarked at download"
                >Executive Summary (PDF)</a>
                <div className="text-[10px] text-gray-400 mt-1">💡 Watermarked at download</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="font-medium text-sm mb-2">Footnotes</div>
            <div className="space-y-1">
              {(footnotes.data||[]).map(fn => (
                <div key={fn.id} className="flex items-center justify-between text-sm">
                  <div>FN {fn.id} <span className="kpi-sub">· updated {new Date(fn.retrievedAt||fn.lastUpdated||Date.now()).toLocaleString()}</span></div>
                  <button className="badge" onClick={()=>setOpenFn(fn.id)}>open</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <Drawer openId={openFn} onClose={()=>setOpenFn(null)} register={footnoteRegister} />
    </div>
  );
}

export default App;