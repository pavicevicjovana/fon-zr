import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import { Plus, Pencil, Trash2, RotateCcw, X, Package, Users, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react';

const initialForm = {
  name: '', description: '', price: '', category: '', collection: '', is_active: true, variants: [],
};
const initialVariant = { size: '', color: '', stock: '' };

function StatCard({ icon: Icon, label, value, sub, color = 'black' }) {
  return (
    <div className="bg-white border border-neutral-200 p-5">
      <div className="flex items-start justify-between mb-3">
        <Icon size={18} className="text-neutral-400" />
        <span className={`text-2xl font-serif font-bold ${color === 'green' ? 'text-green-600' : color === 'red' ? 'text-red-400' : 'text-black'}`}>
          {value}
        </span>
      </div>
      <p className="text-xs tracking-widest uppercase text-neutral-500">{label}</p>
      {sub && <p className="text-xs text-neutral-300 mt-0.5">{sub}</p>}
    </div>
  );
}

function Badge({ active }) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-sm ${
      active ? 'bg-green-50 text-green-700' : 'bg-neutral-100 text-neutral-400'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-green-500' : 'bg-neutral-300'}`} />
      {active ? 'Aktivan' : 'Neaktivan'}
    </span>
  );
}

export default function Admin({ user }) {
  const [tab, setTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [newVariant, setNewVariant] = useState(initialVariant);
  const [submitting, setSubmitting] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    if (!user || user.rola !== 'administrator') return;
    if (tab === 'products') loadProducts();
    if (tab === 'users') loadUsers();
  }, [tab, user]);

  if (!user || user.rola !== 'administrator') {
    return (
      <div className="min-h-screen bg-neutral-50 pt-14 flex items-center justify-center">
        <div className="text-center">
          <XCircle size={32} className="text-neutral-300 mx-auto mb-3" />
          <p className="text-sm text-neutral-400 tracking-widest uppercase">Pristup odbijen</p>
        </div>
      </div>
    );
  }

  const loadProducts = async () => {
    setLoadingProducts(true);
    try {
      const res = await api.get('/admin/products');
      setProducts(res.data);
    } catch { alert('Greška pri učitavanju proizvoda.'); }
    finally { setLoadingProducts(false); }
  };

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      const res = await api.get('/users');
      setUsers(res.data);
    } catch { setUsers([]); }
    finally { setLoadingUsers(false); }
  };

  const openAdd = () => {
    setEditingId(null);
    setForm(initialForm);
    setNewVariant(initialVariant);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const openEdit = (p) => {
    setEditingId(p.id);
    setForm({
      name: p.name || '',
      description: p.description || '',
      price: p.price,
      category: p.category || '',
      collection: p.collection || '',
      is_active: p.is_active,
      variants: p.variants || [],
    });
    setNewVariant(initialVariant);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    setForm(initialForm);
    setNewVariant(initialVariant);
  };

  const addVariant = () => {
    if (!newVariant.size.trim() || !newVariant.color.trim() || !newVariant.stock) return;
    setForm(f => ({
      ...f,
      variants: [...f.variants, {
        size: newVariant.size.trim(),
        color: newVariant.color.trim(),
        stock: parseInt(newVariant.stock),
        sku: `SKU-${Date.now()}`,
      }],
    }));
    setNewVariant(initialVariant);
  };

  const removeVariant = (idx) => setForm(f => ({ ...f, variants: f.variants.filter((_, i) => i !== idx) }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = { ...form, price: parseFloat(form.price) };
      if (editingId) await api.put(`/products/${editingId}`, payload);
      else await api.post('/products', payload);
      closeForm();
      loadProducts();
    } catch (err) {
      alert('Greška: ' + (err.response?.data?.detail || 'Pokušajte ponovo.'));
    } finally { setSubmitting(false); }
  };

  const handleToggleActive = async (p) => {
    if (p.is_active && !window.confirm(`Da li ste sigurni da želite da deaktivirate "${p.name}"?`)) return;
    try {
      if (p.is_active) await api.delete(`/products/${p.id}`);
      else await api.put(`/products/${p.id}`, { is_active: true });
      loadProducts();
    } catch { alert('Greška pri promeni statusa.'); }
  };

  const activeProducts = products.filter(p => p.is_active).length;
  const inactiveProducts = products.length - activeProducts;
  const activeUsers = users.filter(u => u.je_aktivan).length;

  return (
    <div className="min-h-screen bg-neutral-50 pt-14">
      {/* Page header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-screen-xl mx-auto px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Admin panel</h1>
            <p className="text-xs text-neutral-400 mt-0.5">Prijavljeni kao {user.ime} {user.prezime}</p>
          </div>
          <span className="text-xs tracking-widest uppercase text-neutral-300 border border-neutral-200 px-3 py-1.5">
            Administrator
          </span>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 py-8">

        {/* Stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard icon={Package} label="Ukupno proizvoda" value={products.length} />
          <StatCard icon={CheckCircle} label="Aktivni" value={activeProducts} color="green" />
          <StatCard icon={XCircle} label="Neaktivni" value={inactiveProducts} color="red" />
          <StatCard icon={Users} label="Korisnici" value={users.length} sub={`${activeUsers} aktivnih`} />
        </div>

        {/* Tabs */}
        <div className="bg-white border border-neutral-200 mb-0">
          <div className="flex border-b border-neutral-200 px-4">
            {[
              { key: 'products', label: 'Proizvodi', count: products.length },
              { key: 'users', label: 'Korisnici', count: users.length },
            ].map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => { setTab(key); setShowForm(false); }}
                className={`flex items-center gap-2 px-4 py-3.5 text-sm border-b-2 -mb-px transition ${
                  tab === key ? 'border-black text-black font-medium' : 'border-transparent text-neutral-400 hover:text-black'
                }`}
              >
                {label}
                <span className={`text-xs px-1.5 py-0.5 rounded-sm ${
                  tab === key ? 'bg-black text-white' : 'bg-neutral-100 text-neutral-400'
                }`}>
                  {count}
                </span>
              </button>
            ))}
          </div>

          {/* ─── PROIZVODI ─── */}
          {tab === 'products' && (
            <div>
              {/* Toolbar */}
              <div className="flex items-center justify-between px-5 py-3 border-b border-neutral-100">
                <p className="text-xs text-neutral-400">
                  {activeProducts} aktivnih · {inactiveProducts} neaktivnih
                </p>
                {!showForm && (
                  <button
                    onClick={openAdd}
                    className="flex items-center gap-1.5 bg-black text-white text-xs font-medium px-4 py-2 hover:bg-neutral-800 transition"
                  >
                    <Plus size={13} /> Novi proizvod
                  </button>
                )}
              </div>

              {/* ── Forma ── */}
              {showForm && (
                <div className="border-b border-neutral-200 bg-neutral-50">
                  <div className="px-5 py-4 flex items-center justify-between border-b border-neutral-200 bg-white">
                    <div>
                      <h2 className="text-sm font-semibold">
                        {editingId ? 'Uredi proizvod' : 'Novi proizvod'}
                      </h2>
                      <p className="text-xs text-neutral-400 mt-0.5">
                        {editingId ? 'Izmijeni podatke i varijante' : 'Popunite sve obavezne podatke'}
                      </p>
                    </div>
                    <button onClick={closeForm} className="p-1.5 hover:bg-neutral-100 transition rounded-sm">
                      <X size={16} className="text-neutral-400" />
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="p-5 space-y-5">
                    {/* Sekcija: Osnovno */}
                    <div>
                      <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400 mb-3">
                        Osnovni podaci
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="md:col-span-3">
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Naziv *</label>
                          <input
                            required
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
                            value={form.name}
                            onChange={e => setForm({ ...form, name: e.target.value })}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Cijena (RSD) *</label>
                          <input
                            required type="number" min="0" step="0.01"
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
                            value={form.price}
                            onChange={e => setForm({ ...form, price: e.target.value })}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Kategorija *</label>
                          <input
                            required placeholder="Odeca, Obuca, Dodaci..."
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
                            value={form.category}
                            onChange={e => setForm({ ...form, category: e.target.value })}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Kolekcija</label>
                          <input
                            placeholder="Leto, Zima, Premium..."
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
                            value={form.collection}
                            onChange={e => setForm({ ...form, collection: e.target.value })}
                          />
                        </div>
                        <div className="md:col-span-3">
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Opis</label>
                          <textarea
                            rows={2}
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition resize-none"
                            value={form.description}
                            onChange={e => setForm({ ...form, description: e.target.value })}
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-neutral-500 mb-1 font-medium">Status</label>
                          <select
                            className="w-full bg-white border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
                            value={String(form.is_active)}
                            onChange={e => setForm({ ...form, is_active: e.target.value === 'true' })}
                          >
                            <option value="true">Aktivan</option>
                            <option value="false">Neaktivan</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    {/* Sekcija: Varijante */}
                    <div className="border-t border-neutral-200 pt-5">
                      <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400 mb-3">
                        Varijante · {form.variants.length} dodato
                      </p>

                      {form.variants.length > 0 && (
                        <div className="bg-white border border-neutral-200 mb-3 overflow-hidden">
                          <div className="grid grid-cols-12 bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                            {['Veličina', 'Boja', 'Zalihe', 'SKU', ''].map((h, i) => (
                              <span key={i} className={`text-xs font-medium text-neutral-400 uppercase tracking-wider col-span-${i === 4 ? 1 : 3} ${i === 4 ? 'text-right' : ''}`}>{h}</span>
                            ))}
                          </div>
                          {form.variants.map((v, i) => (
                            <div key={i} className="grid grid-cols-12 items-center px-3 py-2.5 border-b border-neutral-100 last:border-0 hover:bg-neutral-50 transition text-sm">
                              <span className="col-span-3 font-medium">{v.size}</span>
                              <span className="col-span-3 text-neutral-600">{v.color}</span>
                              <span className="col-span-3 text-neutral-600">{v.stock} kom</span>
                              <span className="col-span-2 text-xs text-neutral-300 font-mono">{v.sku}</span>
                              <div className="col-span-1 flex justify-end">
                                <button type="button" onClick={() => removeVariant(i)}
                                  className="p-1 hover:bg-red-50 hover:text-red-500 transition rounded-sm">
                                  <X size={13} />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex gap-2">
                        <input placeholder="Veličina" className="flex-1 bg-white border border-neutral-300 px-3 py-2 text-xs focus:outline-none focus:border-black transition"
                          value={newVariant.size} onChange={e => setNewVariant({ ...newVariant, size: e.target.value })} />
                        <input placeholder="Boja" className="flex-1 bg-white border border-neutral-300 px-3 py-2 text-xs focus:outline-none focus:border-black transition"
                          value={newVariant.color} onChange={e => setNewVariant({ ...newVariant, color: e.target.value })} />
                        <input type="number" placeholder="Zalihe" min="0" className="flex-1 bg-white border border-neutral-300 px-3 py-2 text-xs focus:outline-none focus:border-black transition"
                          value={newVariant.stock} onChange={e => setNewVariant({ ...newVariant, stock: e.target.value })} />
                        <button type="button" onClick={addVariant}
                          className="bg-white border border-black text-xs font-medium px-4 py-2 hover:bg-black hover:text-white transition whitespace-nowrap">
                          + Dodaj
                        </button>
                      </div>
                    </div>

                    {/* Akcije forme */}
                    <div className="flex gap-3 pt-2 border-t border-neutral-200">
                      <button type="submit" disabled={submitting}
                        className="flex-1 bg-black text-white text-xs font-medium tracking-wide py-3 hover:bg-neutral-800 transition disabled:opacity-50">
                        {submitting ? 'Čuvanje...' : editingId ? 'Sačuvaj izmjene' : 'Dodaj proizvod'}
                      </button>
                      <button type="button" onClick={closeForm}
                        className="border border-neutral-300 text-xs font-medium px-8 py-3 hover:border-black hover:text-black transition text-neutral-500">
                        Otkaži
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* ── Tabela proizvoda ── */}
              {loadingProducts ? (
                <div className="text-center py-16 text-xs text-neutral-300 uppercase tracking-widest">Učitavanje...</div>
              ) : products.length === 0 ? (
                <div className="text-center py-16 text-xs text-neutral-300 uppercase tracking-widest">Nema proizvoda</div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 text-left">
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400 w-10">#</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Naziv</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Kategorija</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Kolekcija</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400 text-right">Cijena</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400 text-center">Zalihe</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Status</th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400 text-right">Akcije</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p, idx) => {
                      const variants = p.variants || [];
                      const totalStock = variants.reduce((sum, v) => sum + (v.stock || 0), 0);
                      const isExpanded = expandedId === p.id;
                      const lowStock = totalStock > 0 && totalStock <= 5;
                      const outOfStock = totalStock === 0 && variants.length > 0;
                      return (
                        <>
                          <tr key={p.id} className={`border-b border-neutral-100 hover:bg-neutral-50 transition ${!p.is_active ? 'opacity-50' : ''}`}>
                            <td className="px-5 py-3.5 text-xs text-neutral-300">{idx + 1}</td>
                            <td className="px-3 py-3.5">
                              <p className="font-medium text-sm">{p.name}</p>
                              {p.description && (
                                <p className="text-xs text-neutral-400 mt-0.5 max-w-xs truncate">{p.description}</p>
                              )}
                            </td>
                            <td className="px-3 py-3.5 text-xs text-neutral-500">{p.category}</td>
                            <td className="px-3 py-3.5 text-xs text-neutral-400">{p.collection || <span className="text-neutral-200">—</span>}</td>
                            <td className="px-3 py-3.5 text-sm font-medium text-right whitespace-nowrap">
                              {Number(p.price).toLocaleString()} <span className="text-xs text-neutral-400 font-normal">RSD</span>
                            </td>
                            <td className="px-3 py-3.5 text-center">
                              <button
                                onClick={() => setExpandedId(isExpanded ? null : p.id)}
                                className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 transition hover:opacity-70"
                                title="Prikaži zalihe po varijantama"
                              >
                                <span className={`${outOfStock ? 'text-red-500' : lowStock ? 'text-amber-500' : 'text-neutral-600'}`}>
                                  {totalStock} kom
                                </span>
                                <span className="text-neutral-300">·</span>
                                <span className="text-neutral-400">{variants.length} var.</span>
                                {isExpanded
                                  ? <ChevronDown size={11} className="text-neutral-400" />
                                  : <ChevronRight size={11} className="text-neutral-300" />}
                              </button>
                            </td>
                            <td className="px-3 py-3.5"><Badge active={p.is_active} /></td>
                            <td className="px-5 py-3.5">
                              <div className="flex items-center justify-end gap-1.5">
                                <button onClick={() => openEdit(p)} title="Uredi"
                                  className="flex items-center gap-1 text-xs text-neutral-500 border border-neutral-200 px-2.5 py-1.5 hover:border-black hover:text-black transition">
                                  <Pencil size={11} /> Uredi
                                </button>
                                <button onClick={() => handleToggleActive(p)}
                                  title={p.is_active ? 'Deaktiviraj' : 'Aktiviraj'}
                                  className={`flex items-center gap-1 text-xs border px-2.5 py-1.5 transition ${
                                    p.is_active
                                      ? 'border-neutral-200 text-neutral-500 hover:border-red-300 hover:text-red-500 hover:bg-red-50'
                                      : 'border-neutral-200 text-neutral-500 hover:border-green-400 hover:text-green-600 hover:bg-green-50'
                                  }`}>
                                  {p.is_active ? <><Trash2 size={11} /> Deaktiviraj</> : <><RotateCcw size={11} /> Aktiviraj</>}
                                </button>
                              </div>
                            </td>
                          </tr>
                          {isExpanded && variants.length > 0 && (
                            <tr key={`${p.id}-variants`} className="border-b border-neutral-100 bg-neutral-50">
                              <td colSpan={8} className="px-12 py-3">
                                <table className="w-full text-xs">
                                  <thead>
                                    <tr className="text-left border-b border-neutral-200">
                                      <th className="pb-2 font-semibold text-neutral-400 uppercase tracking-widest pr-8">Veličina</th>
                                      <th className="pb-2 font-semibold text-neutral-400 uppercase tracking-widest pr-8">Boja</th>
                                      <th className="pb-2 font-semibold text-neutral-400 uppercase tracking-widest pr-8">SKU</th>
                                      <th className="pb-2 font-semibold text-neutral-400 uppercase tracking-widest text-right">Na zalihama</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-neutral-100">
                                    {variants.map((v, i) => (
                                      <tr key={i} className="hover:bg-neutral-100 transition">
                                        <td className="py-2 pr-8 font-medium text-neutral-700">{v.size}</td>
                                        <td className="py-2 pr-8 text-neutral-500">{v.color}</td>
                                        <td className="py-2 pr-8 font-mono text-neutral-300">{v.sku || '—'}</td>
                                        <td className="py-2 text-right">
                                          <span className={`font-semibold ${
                                            v.stock === 0 ? 'text-red-500' : v.stock <= 3 ? 'text-amber-500' : 'text-green-600'
                                          }`}>
                                            {v.stock}
                                          </span>
                                          <span className="text-neutral-400 ml-1">kom</span>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                  <tfoot>
                                    <tr className="border-t border-neutral-200">
                                      <td colSpan={3} className="pt-2 text-neutral-400 font-medium uppercase tracking-widest">Ukupno</td>
                                      <td className="pt-2 text-right font-bold text-neutral-700">{totalStock} <span className="font-normal text-neutral-400">kom</span></td>
                                    </tr>
                                  </tfoot>
                                </table>
                              </td>
                            </tr>
                          )}
                        </>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* ─── KORISNICI ─── */}
          {tab === 'users' && (
            <div>
              <div className="px-5 py-3 border-b border-neutral-100">
                <p className="text-xs text-neutral-400">
                  {users.filter(u => u.je_aktivan).length} aktivnih · {users.filter(u => !u.je_aktivan).length} neaktivnih
                </p>
              </div>

              {loadingUsers ? (
                <div className="text-center py-16 text-xs text-neutral-300 uppercase tracking-widest">Učitavanje...</div>
              ) : users.length === 0 ? (
                <div className="text-center py-16 text-xs text-neutral-300 uppercase tracking-widest">Nema korisnika</div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 text-left">
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">ID</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Ime i prezime</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Email</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Telefon</th>
                      <th className="px-3 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Rola</th>
                      <th className="px-5 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100">
                    {users.map(u => (
                      <tr key={u.id} className="hover:bg-neutral-50 transition">
                        <td className="px-5 py-3.5 text-xs text-neutral-300 font-mono">#{u.id}</td>
                        <td className="px-3 py-3.5">
                          <p className="font-medium">{u.ime} {u.prezime}</p>
                        </td>
                        <td className="px-3 py-3.5 text-neutral-500">{u.email}</td>
                        <td className="px-3 py-3.5 text-xs text-neutral-400">{u.broj_telefona || <span className="text-neutral-200">—</span>}</td>
                        <td className="px-3 py-3.5">
                          {u.rola === 'administrator' ? (
                            <span className="inline-block bg-black text-white text-xs font-medium px-2 py-0.5 tracking-wide">
                              Admin
                            </span>
                          ) : (
                            <span className="text-xs text-neutral-400">Korisnik</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5"><Badge active={u.je_aktivan} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
