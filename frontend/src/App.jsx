import { useEffect, useMemo, useState } from 'react';
import './index.css';

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function apiFetch(path, { token, method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const url = path.startsWith('http') ? path : `${apiBase}${path}`;
  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

function App() {
  const [health, setHealth] = useState({ status: 'checking', message: 'Memeriksa API...' });
  const [token, setToken] = useState('');
  const [authForm, setAuthForm] = useState({ email: '', password: '' });
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [txMeta, setTxMeta] = useState({ page: 1, page_size: 10, total_pages: 1, total_items: 0 });
  const [txFilters, setTxFilters] = useState({ q: '', type: '', category_id: '', start_date: '', end_date: '' });
  const [accountForm, setAccountForm] = useState({ name: '', type: 'cash', currency: 'IDR' });
  const [categoryForm, setCategoryForm] = useState({ name: '', type: 'expense' });
  const [txForm, setTxForm] = useState({
    account_id: '',
    category_id: '',
    type: 'expense',
    amount: 0,
    currency: 'IDR',
    description: '',
    occurred_at: new Date().toISOString(),
    status: 'confirmed',
    source: 'manual',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState({ show: false, message: '', tone: 'error' });

  const showToast = (message, tone = 'error', timeout = 4000) => {
    setToast({ show: true, message, tone });
    setTimeout(() => setToast({ show: false, message: '', tone: 'error' }), timeout);
  };

  const isAuthed = useMemo(() => Boolean(token), [token]);
  const currentPeriod = useMemo(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  }, []);
  const [period, setPeriod] = useState(currentPeriod);

  const buildTxParams = (page = 1, overrides = {}) => {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', String(txMeta.page_size || 10));
    Object.entries({ ...txFilters, ...overrides }).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    return params.toString();
  };

  const loadTransactions = async (page = 1, overrides = {}) => {
    if (!isAuthed) return;
    const query = buildTxParams(page, overrides);
    const data = await apiFetch(`/transactions?${query}`, { token });
    setTransactions(data.items || data);
    if (data.pagination) setTxMeta(data.pagination);
  };

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBase}/health`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setHealth({ status: 'ok', message: data.status || 'ok' });
      })
      .catch((err) => setHealth({ status: 'fail', message: err.message }));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!isAuthed) return;
    const loadData = async () => {
      try {
        setLoading(true);
        const [acc, cats, txs, sum] = await Promise.all([
          apiFetch('/accounts', { token }),
          apiFetch('/categories', { token }),
          apiFetch(`/transactions?${buildTxParams(1)}`, { token }),
          apiFetch(`/dashboard/summary?period=${period}`, { token }),
        ]);
        setAccounts(acc);
        setCategories(cats);
        setTransactions(txs.items || txs);
        if (txs.pagination) setTxMeta(txs.pagination);
        setSummary(sum);
        if (acc.length > 0) setTxForm((f) => ({ ...f, account_id: f.account_id || acc[0].id }));
        if (cats.length > 0) setTxForm((f) => ({ ...f, category_id: f.category_id || cats[0].id }));
      } catch (e) {
        setError(e.message);
        showToast(e.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [isAuthed, token, period]);

  const refreshSummary = async (p = period) => {
    if (!isAuthed) return;
    setSummaryLoading(true);
    try {
      const sum = await apiFetch(`/dashboard/summary?period=${p}`, { token });
      setSummary(sum);
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleRegister = async () => {
    setError('');
    try {
      await apiFetch('/auth/register', { method: 'POST', body: authForm });
      await handleLogin();
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    }
  };

  const handleLogin = async () => {
    setError('');
    try {
      const data = await apiFetch('/auth/login', { method: 'POST', body: authForm });
      setToken(data.access_token);
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    }
  };

  const handleCreateAccount = async () => {
    if (!accountForm.name) return;
    setError('');
    try {
      const acc = await apiFetch('/accounts', { method: 'POST', body: accountForm, token });
      setAccounts((prev) => [...prev, acc]);
      setAccountForm({ name: '', type: 'cash', currency: 'IDR' });
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    }
  };

  const handleCreateCategory = async () => {
    if (!categoryForm.name) return;
    setError('');
    try {
      const cat = await apiFetch('/categories', { method: 'POST', body: categoryForm, token });
      setCategories((prev) => [...prev, cat]);
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    }
  };

  const handleCreateTx = async () => {
    if (!txForm.account_id || !txForm.type || !txForm.occurred_at) return;
    setError('');
    try {
      const tx = await apiFetch('/transactions', { method: 'POST', body: txForm, token });
      setTransactions((prev) => [tx, ...prev]);
    } catch (e) {
      setError(e.message);
      showToast(e.message);
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-ink-900">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-ink-500">Sprint 1 — Frontend</p>
            <h1 className="mt-2 text-3xl font-bold text-ink-900 sm:text-4xl">FinTrack Dashboard (Vite + React + Tailwind)</h1>
            <p className="mt-2 max-w-2xl text-sm text-ink-500">Fondasi UI terhubung ke API untuk auth, akun, kategori, dan transaksi.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-lime-500/20 px-3 py-1 text-xs font-semibold text-lime-600">Podman Ready</span>
            <span className="rounded-full bg-ink-100 px-3 py-1 text-xs font-semibold text-ink-700">MVP Scope</span>
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                health.status === 'ok' ? 'bg-lime-500/20 text-lime-700' : 'bg-red-100 text-red-700'
              }`}
            >
              API: {health.message}
            </span>
            {isAuthed && <span className="rounded-full bg-ink-100 px-3 py-1 text-xs font-semibold text-ink-700">Token aktif</span>}
          </div>
        </header>

        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        {toast.show && (
          <div
            className={`fixed right-4 top-4 z-50 max-w-sm rounded-lg px-4 py-3 text-sm shadow-lg ${
              toast.tone === 'error' ? 'bg-red-100 text-red-800 border border-red-200' : 'bg-lime-100 text-lime-800 border border-lime-200'
            }`}
          >
            {toast.message}
          </div>
        )}

        {/* Auth block */}
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink-900">Auth & Session</h2>
              <span className="text-xs font-semibold text-lime-600">{isAuthed ? 'Logged in' : 'v0'}</span>
            </div>
            <p className="mt-2 text-sm text-ink-500">Terhubung ke /auth/register & /auth/login.</p>
            <form className="mt-4 flex flex-col gap-3" onSubmit={(e) => e.preventDefault()}>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-ink-700" htmlFor="email">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm((f) => ({ ...f, email: e.target.value }))}
                  placeholder="you@example.com"
                  className="rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm text-ink-900 shadow-sm outline-none transition focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-ink-700" htmlFor="password">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm((f) => ({ ...f, password: e.target.value }))}
                  placeholder="••••••••"
                  className="rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm text-ink-900 shadow-sm outline-none transition focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleLogin}
                  className="flex-1 rounded-lg bg-ink-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-ink-700"
                >
                  Login
                </button>
                <button
                  type="button"
                  onClick={handleRegister}
                  className="flex-1 rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm font-semibold text-ink-900 transition hover:border-lime-500 hover:text-lime-600"
                >
                  Register
                </button>
              </div>
            </form>
            <p className="mt-3 text-xs text-ink-500">Token disimpan in-memory; tambahkan refresh/secure storage nanti.</p>
          </div>

          {/* Accounts and categories */}
          <div className="rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink-900">Akun & Kategori</h2>
              <span className="text-xs font-semibold text-ink-500">Sprint 1</span>
            </div>
            <div className="mt-3 flex flex-col gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Akun</p>
                <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {accounts.map((acc) => (
                    <div key={acc.id} className="rounded-xl border border-ink-100 bg-white px-3 py-3 shadow-sm">
                      <div className="flex items-center justify-between text-sm font-semibold text-ink-900">
                        <span>{acc.name}</span>
                        <span className="text-xs text-ink-500">{acc.type}</span>
                      </div>
                      <p className="mt-1 text-sm text-ink-700">{acc.currency}</p>
                    </div>
                  ))}
                  {accounts.length === 0 && <p className="text-xs text-ink-500">Belum ada akun.</p>}
                </div>
                <div className="mt-3 flex gap-2">
                  <input
                    className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm outline-none transition focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                    placeholder="Nama akun"
                    value={accountForm.name}
                    onChange={(e) => setAccountForm((f) => ({ ...f, name: e.target.value }))}
                  />
                  <select
                    className="rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                    value={accountForm.type}
                    onChange={(e) => setAccountForm((f) => ({ ...f, type: e.target.value }))}
                  >
                    <option value="cash">cash</option>
                    <option value="bank">bank</option>
                    <option value="e-wallet">e-wallet</option>
                  </select>
                  <button
                    type="button"
                    onClick={handleCreateAccount}
                    className="rounded-lg bg-ink-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-ink-700"
                  >
                    Simpan
                  </button>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Kategori</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <span key={cat.id} className="rounded-full bg-ink-100 px-3 py-1 text-xs font-semibold text-ink-700">
                      {cat.type}: {cat.name}
                    </span>
                  ))}
                  {categories.length === 0 && <p className="text-xs text-ink-500">Belum ada kategori.</p>}
                </div>
                <div className="mt-3 flex gap-2">
                  <input
                    className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm outline-none transition focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                    placeholder="Nama kategori"
                    value={categoryForm.name}
                    onChange={(e) => setCategoryForm((f) => ({ ...f, name: e.target.value }))}
                  />
                  <select
                    className="rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                    value={categoryForm.type}
                    onChange={(e) => setCategoryForm((f) => ({ ...f, type: e.target.value }))}
                  >
                    <option value="income">income</option>
                    <option value="expense">expense</option>
                    <option value="transfer">transfer</option>
                  </select>
                  <button
                    type="button"
                    onClick={handleCreateCategory}
                    className="rounded-lg bg-ink-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-ink-700"
                  >
                    Simpan
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Checklist */}
          <div className="rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink-900">Exit Checklist</h2>
              <span className="text-xs font-semibold text-lime-600">Go/No-Go</span>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-ink-700">
              <li>{health.status === 'ok' ? '✅' : '⚠️'} Healthcheck 200</li>
              <li>{isAuthed ? '✅' : '⚠️'} Login/Register berfungsi</li>
              <li>{accounts.length > 0 ? '✅' : '⚠️'} Akun CRUD (create + list)</li>
              <li>{categories.length > 0 ? '✅' : '⚠️'} Kategori CRUD (create + list)</li>
              <li>{transactions.length > 0 ? '✅' : '⚠️'} Transaksi create/read</li>
            </ul>
            <div className="mt-4 rounded-xl border border-ink-100 bg-ink-100 px-3 py-2 text-xs text-ink-700">
              Jika ada P1 blocking (auth gagal, API tidak jalan), tetap di Sprint 1 untuk perbaikan.
            </div>
          </div>
        </section>

        {/* Transactions */}
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink-900">Dashboard</h2>
              <div className="flex items-center gap-2">
                <input
                  type="month"
                  value={period}
                  onChange={(e) => {
                    const val = e.target.value;
                    setPeriod(val);
                    refreshSummary(val);
                  }}
                  className="rounded-lg border border-ink-100 bg-white px-2 py-1 text-xs text-ink-900 outline-none focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                />
                <button
                  type="button"
                  onClick={() => refreshSummary(period)}
                  className="rounded-lg border border-ink-100 bg-white px-2 py-1 text-xs font-semibold text-ink-700 transition hover:border-lime-500 hover:text-lime-600"
                >
                  Refresh
                </button>
              </div>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-ink-100 bg-white px-3 py-3 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Income</p>
                <p className="mt-1 text-lg font-bold text-lime-700">
                  Rp{summary ? summary.income.toLocaleString('id-ID') : summaryLoading ? '...' : '0'}
                </p>
              </div>
              <div className="rounded-xl border border-ink-100 bg-white px-3 py-3 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Expense</p>
                <p className="mt-1 text-lg font-bold text-red-600">
                  Rp{summary ? summary.expense.toLocaleString('id-ID') : summaryLoading ? '...' : '0'}
                </p>
              </div>
              <div className="rounded-xl border border-ink-100 bg-white px-3 py-3 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Balance</p>
                <p className="mt-1 text-lg font-bold text-ink-900">
                  Rp{summary ? summary.balance.toLocaleString('id-ID') : summaryLoading ? '...' : '0'}
                </p>
              </div>
            </div>
            <div className="mt-5">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Top Kategori (Expense)</p>
              <div className="mt-2 flex flex-col gap-2">
                {(summary?.top_categories || []).map((cat) => {
                  const total = cat.total || 0;
                  const max = (summary?.top_categories?.[0]?.total || 1) || 1;
                  const percent = Math.min(100, Math.round((total / max) * 100));
                  return (
                    <div key={cat.category_id || cat.name} className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs text-ink-700">
                        <span>{cat.name || 'Uncategorized'}</span>
                        <span>Rp{total.toLocaleString('id-ID')}</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-ink-100">
                        <div
                          className="h-2 rounded-full bg-lime-500 transition-all"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
                {summary && summary.top_categories?.length === 0 && (
                  <p className="text-xs text-ink-500">Belum ada data kategori.</p>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink-900">Transaksi</h2>
              <span className="text-xs font-semibold text-ink-500">Manual Input</span>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-ink-700">
              <input
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-sm outline-none focus:border-lime-500 focus:ring-2 focus:ring-lime-500/30"
                placeholder="Cari deskripsi"
                value={txFilters.q}
                onChange={(e) => setTxFilters((f) => ({ ...f, q: e.target.value }))}
              />
              <select
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-sm"
                value={txFilters.type}
                onChange={(e) => setTxFilters((f) => ({ ...f, type: e.target.value }))}
              >
                <option value="">Semua tipe</option>
                <option value="income">income</option>
                <option value="expense">expense</option>
                <option value="transfer">transfer</option>
              </select>
              <select
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-sm"
                value={txFilters.category_id}
                onChange={(e) => setTxFilters((f) => ({ ...f, category_id: e.target.value }))}
              >
                <option value="">Semua kategori</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              <input
                type="date"
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-sm"
                value={txFilters.start_date}
                onChange={(e) => setTxFilters((f) => ({ ...f, start_date: e.target.value }))}
              />
              <input
                type="date"
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-sm"
                value={txFilters.end_date}
                onChange={(e) => setTxFilters((f) => ({ ...f, end_date: e.target.value }))}
              />
              <button
                type="button"
                onClick={() => loadTransactions(1)}
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-xs font-semibold text-ink-700 transition hover:border-lime-500 hover:text-lime-600"
              >
                Apply
              </button>
              <button
                type="button"
                onClick={() => {
                  const reset = { q: '', type: '', category_id: '', start_date: '', end_date: '' };
                  setTxFilters(reset);
                  loadTransactions(1, reset);
                }}
                className="rounded-lg border border-ink-100 bg-white px-3 py-1.5 text-xs font-semibold text-ink-700 transition hover:border-lime-500 hover:text-lime-600"
              >
                Reset
              </button>
            </div>
            <div className="mt-3 overflow-hidden rounded-xl border border-ink-100">
              <table className="min-w-full divide-y divide-ink-100 text-sm">
                <thead className="bg-ink-100/50 text-ink-700">
                  <tr>
                    <th className="px-3 py-2 text-left font-semibold">Deskripsi</th>
                    <th className="px-3 py-2 text-left font-semibold">Tipe</th>
                    <th className="px-3 py-2 text-left font-semibold">Jumlah</th>
                    <th className="px-3 py-2 text-left font-semibold">Tanggal</th>
                    <th className="px-3 py-2 text-left font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100 bg-white">
                  {transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td className="px-3 py-2 font-semibold text-ink-900">{tx.description || '-'}</td>
                      <td className="px-3 py-2 text-ink-700">{tx.type}</td>
                      <td className="px-3 py-2 text-ink-900">
                        {tx.type === 'expense' ? '-' : '+'}
                        {tx.amount}
                      </td>
                      <td className="px-3 py-2 text-ink-700">{tx.occurred_at?.slice(0, 10)}</td>
                      <td className="px-3 py-2">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                            tx.status === 'confirmed' ? 'bg-lime-500/20 text-lime-700' : 'bg-ink-100 text-ink-700'
                          }`}
                        >
                          {tx.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {transactions.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-3 py-2 text-center text-xs text-ink-500">
                        Belum ada transaksi.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-ink-700">
              <div>
                Page {txMeta.page} / {txMeta.total_pages || 1} (Total {txMeta.total_items || transactions.length} transaksi)
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={txMeta.page <= 1}
                  onClick={() => loadTransactions(txMeta.page - 1)}
                  className="rounded-lg border border-ink-100 bg-white px-2 py-1 font-semibold transition hover:border-lime-500 hover:text-lime-600 disabled:opacity-50"
                >
                  Prev
                </button>
                <button
                  type="button"
                  disabled={txMeta.page >= (txMeta.total_pages || 1)}
                  onClick={() => loadTransactions(txMeta.page + 1)}
                  className="rounded-lg border border-ink-100 bg-white px-2 py-1 font-semibold transition hover:border-lime-500 hover:text-lime-600 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-ink-100 bg-white/70 p-5 shadow-sm backdrop-blur">
            <h2 className="text-lg font-semibold text-ink-900">Buat Transaksi</h2>
            <div className="mt-3 space-y-3 text-sm text-ink-700">
              <select
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                value={txForm.account_id}
                onChange={(e) => setTxForm((f) => ({ ...f, account_id: e.target.value }))}
              >
                <option value="">Pilih akun</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name}
                  </option>
                ))}
              </select>
              <select
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                value={txForm.category_id}
                onChange={(e) => setTxForm((f) => ({ ...f, category_id: e.target.value }))}
              >
                <option value="">Pilih kategori</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              <select
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                value={txForm.type}
                onChange={(e) => setTxForm((f) => ({ ...f, type: e.target.value }))}
              >
                <option value="income">income</option>
                <option value="expense">expense</option>
                <option value="transfer">transfer</option>
              </select>
              <input
                type="number"
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                placeholder="Jumlah"
                value={txForm.amount}
                onChange={(e) => setTxForm((f) => ({ ...f, amount: parseFloat(e.target.value) || 0 }))}
              />
              <input
                type="text"
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                placeholder="Deskripsi"
                value={txForm.description}
                onChange={(e) => setTxForm((f) => ({ ...f, description: e.target.value }))}
              />
              <input
                type="datetime-local"
                className="w-full rounded-lg border border-ink-100 bg-white px-3 py-2 text-sm"
                value={txForm.occurred_at.slice(0, 16)}
                onChange={(e) => setTxForm((f) => ({ ...f, occurred_at: new Date(e.target.value).toISOString() }))}
              />
              <button
                type="button"
                onClick={handleCreateTx}
                disabled={!isAuthed || loading}
                className="w-full rounded-lg bg-ink-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-ink-700 disabled:opacity-50"
              >
                {loading ? 'Menyimpan...' : 'Tambah Transaksi'}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
