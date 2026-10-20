import { useEffect, useMemo, useState } from 'react'
import './App.css'

const api = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  const body = await response.json().catch(() => null)
  if (!response.ok) throw new Error(body?.detail ? (typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)) : `HTTP ${response.status}`)
  return body
}
const money = (value) => new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 2 }).format(Number(value || 0)) + ' TL'
const normalizeCustomers = (payload) => Array.isArray(payload) ? payload : payload?.customers || payload?.items || []
const getId = (customer) => customer.id ?? customer.customer_id ?? customer.subscription_id
const gb = (customer) => customer.current_gb ?? customer.main_prod_tariff_gb ?? 0
const price = (customer) => customer.current_price ?? customer.main_prod_tariff_price ?? 0

export default function App() {
  const [customers, setCustomers] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [acceptance, setAcceptance] = useState(null)
  const [error, setError] = useState('')
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    api('/customers')
      .then((data) => { const list = normalizeCustomers(data); setCustomers(list); setSelectedId(list.length ? getId(list[0]) : null); setConnected(true) })
      .catch((err) => { setError(`Backend bağlantısı kurulamadı: ${err.message}`); setConnected(false) })
      .finally(() => setLoading(false))
  }, [])

  const selected = customers.find((customer) => String(getId(customer)) === String(selectedId))
  const filtered = useMemo(() => customers.filter((customer) => String(getId(customer)).includes(query.trim())), [customers, query])
  const offers = result?.offers || []
  const runId = result?.run_id

  const chooseCustomer = (id) => { setSelectedId(id); setResult(null); setAcceptance(null); setError('') }

  const recommend = async () => {
    if (selectedId == null) return
    setBusy(true); setError(''); setResult(null); setAcceptance(null)
    try { setResult(await api(`/customers/${encodeURIComponent(selectedId)}/recommendations`, { method: 'POST' })) }
    catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  const accept = async (tariffId) => {
    if (!runId) { setError('Önce öneri oluşturmalısın.'); return }
    setBusy(true); setError('')
    try { setAcceptance(await api(`/recommendation-runs/${encodeURIComponent(runId)}/acceptances`, { method: 'POST', body: JSON.stringify({ tariff_id: tariffId }) })) }
    catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-icon">✦</div><div><strong>SMART OFFER</strong><span>Recommendation Studio</span></div></div>
      <div className="nav-label">WORKSPACE</div>
      <div className="nav-active">◈ &nbsp; Customer Explorer</div>
      <div className="sidebar-foot"><span className={connected ? 'dot online' : 'dot'} /> {connected ? 'Backend connected' : 'Backend offline'}<small>FastAPI · Local development</small></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><span className="eyebrow">CUSTOMER INTELLIGENCE / OVERVIEW</span><h1>Smart Offer <em>Recommendation</em></h1><p>Explore customers, generate personalized offers and measure revenue uplift.</p></div><div className="top-pill">✧ &nbsp; DEMO ENVIRONMENT</div></header>
      <section className="stats"><div className="stat"><span>Customers</span><strong>{customers.length}</strong><small>Available profiles</small></div><div className="stat"><span>Current plan</span><strong>{selected ? `${gb(selected)} GB` : '—'}</strong><small>{selected ? money(price(selected)) : 'Select a customer'}</small></div><div className="stat"><span>Offers generated</span><strong>{offers.length}</strong><small>Current recommendation run</small></div><div className="stat accent"><span>Accepted uplift</span><strong>{acceptance ? `+${money(acceptance.uplift)}` : '—'}</strong><small>{acceptance ? `+${acceptance.uplift_pct}% versus current price` : 'Awaiting acceptance'}</small></div></section>
      {error && <div role="alert" className="error">⚠ {error}</div>}
      <div className="columns"><section className="panel customer-panel"><div className="panel-head"><div><h2>Customers</h2><p>Choose a customer to explore</p></div><span className="count">{filtered.length}</span></div><input className="search" aria-label="Search customer ID" placeholder="⌕  Search customer ID..." value={query} onChange={(e) => setQuery(e.target.value)} /><div className="customer-list">{loading && <p className="muted">Loading customers...</p>}{!loading && filtered.length === 0 && <p className="muted">No customers found.</p>}{filtered.map((customer) => <button key={getId(customer)} className={`customer-row ${String(getId(customer)) === String(selectedId) ? 'selected' : ''}`} onClick={() => chooseCustomer(getId(customer))}><span className="avatar">{String(getId(customer)).slice(-2)}</span><span className="customer-info"><strong>Customer #{getId(customer)}</strong><small>{gb(customer)} GB · {money(price(customer))}</small></span><span className="chevron">›</span></button>)}</div></section>
      <section className="workspace"><div className="panel profile"><div className="panel-head"><div><span className="eyebrow">SELECTED PROFILE</span><h2>{selected ? `Customer #${getId(selected)}` : 'Select a customer'}</h2></div><span className="badge">SYNTHETIC DATA</span></div><div className="profile-grid"><div><span>Current allowance</span><strong>{selected ? `${gb(selected)} GB` : '—'}</strong></div><div><span>Monthly price</span><strong>{selected ? money(price(selected)) : '—'}</strong></div><div><span>Actual usage</span><strong>{selected ? `${selected.usage_gb ?? '—'} GB` : '—'}</strong></div></div><button className="primary" disabled={!selected || busy} onClick={recommend}>{busy ? 'Processing...' : '✦  Generate 4 recommendations'} <span>→</span></button></div>
      <div className="panel recommendations"><div className="panel-head"><div><h2>Recommended offers</h2><p>Eligibility-checked offers, ranked by the backend</p></div>{result && <span className={`badge ${result.status === 'success' ? 'green' : 'amber'}`}>{result.status}</span>}</div>
      {!result && <div className="empty"><div className="empty-icon">✧</div><h3>Ready to discover better offers</h3><p>Select a customer and generate recommendations to view personalized tariffs.</p></div>}
      {result && offers.length === 0 && <div className="empty"><h3>No eligible offers</h3><p>{result.reason || 'The recommendation engine did not return eligible tariffs.'}</p></div>}
      {offers.length > 0 && <div className="offers">{offers.map((offer, index) => <article className="offer" key={`${offer.tariff_id}-${index}`}><div className="offer-top"><span className="rank">#{offer.rank ?? index + 1}</span><span className="offer-name">{offer.name ?? `Tariff ${offer.tariff_id}`}</span></div><div className="offer-metrics"><strong>{offer.gb} <small>GB</small></strong><strong>{money(offer.price)}</strong></div><p>{offer.explanation || 'Eligible offer'}</p><button className="accept" disabled={busy || Boolean(acceptance)} onClick={() => accept(offer.tariff_id)}>{acceptance?.tariff_id === offer.tariff_id ? '✓ Accepted' : acceptance ? 'Acceptance recorded' : 'Accept offer →'}</button></article>)}</div>}
      {acceptance && <div className="success" role="status"><strong>✓ Offer accepted successfully</strong><span>Tariff #{acceptance.tariff_id} · Uplift: +{money(acceptance.uplift)} ({acceptance.uplift_pct}%)</span></div>}
      {runId && <p className="run-id">Recommendation run: {runId}</p>}
      </div></section></div><footer>Smart Offer Recommendation · AI Dev Tools Zoomcamp · Synthetic demonstration data</footer>
    </main>
  </div>
}
