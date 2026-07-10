import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { User, Package, MapPin, ChevronDown, ChevronUp, Plus, X, Trash2 } from 'lucide-react';
import CountrySelect from '../components/CountrySelect';

const TABS = [
  { key: 'info', label: 'LIČNI PODACI', Icon: User },
  { key: 'orders', label: 'NARUDŽBINE', Icon: Package },
  { key: 'addresses', label: 'ADRESE', Icon: MapPin },
];

const emptyAddress = {
  ulica: '', kucni_broj: '', sprat: '',
  mesto: { postanski_broj: '', grad: '', drzava: '' },
  tip_adrese: 'kucna', je_podrazumijevana: false,
};

export default function Profile({ user, setUser }) {
  const [tab, setTab] = useState('info');
  const [profil, setProfil] = useState({ ime: '', prezime: '', broj_telefona: '' });
  const [orders, setOrders] = useState([]);
  const [expandedOrder, setExpandedOrder] = useState(null);
  const [orderDetail, setOrderDetail] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAddr, setNewAddr] = useState(emptyAddress);
  const [toast, setToast] = useState(null);
  const navigate = useNavigate();

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    setProfil({ ime: user.ime || '', prezime: user.prezime || '', broj_telefona: user.broj_telefona || '' });
  }, [user]);

  useEffect(() => {
    if (!user) return;
    if (tab === 'orders') loadOrders();
    if (tab === 'addresses') loadAddresses();
  }, [tab]);

  const loadOrders = async () => {
    try {
      const res = await api.get(`/orders/${user.id}`);
      setOrders(res.data);
    } catch (err) {
      if (err.response?.status === 404) setOrders([]);
    }
  };

  const loadAddresses = async () => {
    try {
      const res = await api.get(`/users/${user.id}/adrese`);
      setAddresses(res.data);
    } catch { setAddresses([]); }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const res = await api.put(`/users/${user.id}`, profil);
      const updated = { ...user, ime: res.data.ime, prezime: res.data.prezime, broj_telefona: res.data.broj_telefona, rola: res.data.rola };
      localStorage.setItem('user', JSON.stringify(updated));
      setUser(updated);
      showToast('success', 'Podaci su uspešno ažurirani.');
    } catch { showToast('error', 'Greška pri ažuriranju podataka.'); }
  };

  const toggleOrder = async (orderId) => {
    if (expandedOrder === orderId) { setExpandedOrder(null); setOrderDetail(null); return; }
    try {
      const res = await api.get(`/orders/${user.id}/${orderId}`);
      setOrderDetail(res.data);
      setExpandedOrder(orderId);
    } catch { showToast('error', 'Greška pri učitavanju detalja narudžbine.'); }
  };

  const handleSetDefault = async (adresaId) => {
    try {
      await api.put(`/users/${user.id}/adrese/${adresaId}/podrazumijevana`);
      loadAddresses();
      showToast('success', 'Podrazumevana adresa je promenjena.');
    } catch { showToast('error', 'Greška pri postavljanju podrazumevane adrese.'); }
  };

  const handleDeleteAddress = async (adresaId) => {
    if (!window.confirm('Da li ste sigurni da želite da obrišete ovu adresu?')) return;
    try {
      await api.delete(`/users/${user.id}/adrese/${adresaId}`);
      loadAddresses();
      showToast('success', 'Adresa je obrisana.');
    } catch { showToast('error', 'Greška pri brisanju adrese.'); }
  };

  const handleAddAddress = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/users/${user.id}/adrese`, newAddr);
      setShowAddForm(false);
      setNewAddr(emptyAddress);
      loadAddresses();
      showToast('success', 'Adresa je uspešno dodata.');
    } catch { showToast('error', 'Greška pri dodavanju adrese.'); }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-white pt-14">
      {/* Toast notification */}
      {toast && (
        <div className={`fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 text-xs tracking-widest uppercase font-medium shadow-lg transition-all ${
          toast.type === 'success' ? 'bg-black text-white' : 'bg-red-600 text-white'
        }`}>
          {toast.message}
        </div>
      )}
      <div className="max-w-3xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-10 border-b border-neutral-200 pb-8">
          <h1 className="text-4xl font-serif mb-1">Moj nalog</h1>
          <p className="text-xs tracking-widest uppercase text-neutral-400">{user.email}</p>
        </div>

        {/* Tab navigation */}
        <div className="flex border-b border-neutral-200 mb-10">
          {TABS.map(({ key, label, Icon }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex items-center gap-2 px-5 py-3 text-xs tracking-widest uppercase border-b-2 -mb-px transition ${
                tab === key
                  ? 'border-black text-black'
                  : 'border-transparent text-neutral-400 hover:text-black'
              }`}
            >
              <Icon size={13} />
              {label}
            </button>
          ))}
        </div>

        {/* ── Tab: Lični podaci ── */}
        {tab === 'info' && (
          <form onSubmit={handleUpdateProfile} className="space-y-5 max-w-md">
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-1.5">Ime</label>
              <input
                className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
                value={profil.ime}
                onChange={e => setProfil({ ...profil, ime: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-1.5">Prezime</label>
              <input
                className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
                value={profil.prezime}
                onChange={e => setProfil({ ...profil, prezime: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-1.5">Broj telefona</label>
              <input
                className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
                placeholder="+381..."
                value={profil.broj_telefona}
                onChange={e => setProfil({ ...profil, broj_telefona: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-1.5">Email</label>
              <input
                className="w-full border border-neutral-200 px-4 py-3 text-sm bg-neutral-50 text-neutral-400 cursor-not-allowed"
                value={user.email}
                disabled
              />
            </div>
            <button
              type="submit"
              className="w-full bg-black text-white text-xs tracking-widest uppercase py-3.5 hover:bg-neutral-800 transition"
            >
              SAČUVAJ IZMJENE
            </button>
          </form>
        )}

        {/* ── Tab: Narudžbine ── */}
        {tab === 'orders' && (
          <div className="space-y-2">
            {orders.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-xs tracking-widest uppercase text-neutral-300">Nemate nijednu narudžbinu</p>
              </div>
            ) : orders.map(order => (
              <div key={order.narudzba_id} className="border border-neutral-200">
                <button
                  onClick={() => toggleOrder(order.narudzba_id)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-neutral-50 transition"
                >
                  <div>
                    <p className="text-xs tracking-widest uppercase text-neutral-400 mb-1">
                      Narudžbina #{order.narudzba_id}
                    </p>
                    <p className="text-base font-medium">
                      {Number(order.ukupan_iznos).toLocaleString()} RSD
                    </p>
                    <p className="text-xs text-neutral-400 mt-0.5">
                      {new Date(order.kreirana).toLocaleDateString('sr-Latn-RS')}
                      {' · '}
                      <span className="uppercase">{order.status}</span>
                    </p>
                  </div>
                  {expandedOrder === order.narudzba_id
                    ? <ChevronUp size={16} className="text-neutral-400" />
                    : <ChevronDown size={16} className="text-neutral-400" />
                  }
                </button>

                {expandedOrder === order.narudzba_id && orderDetail && (
                  <div className="border-t border-neutral-200 p-5 bg-neutral-50">
                    <p className="text-xs text-neutral-500 mb-4">
                      <span className="tracking-widest uppercase">Adresa: </span>
                      {orderDetail.adresa_isporuke}
                    </p>
                    <div className="space-y-0 divide-y divide-neutral-200">
                      {orderDetail.stavke?.map((s, i) => (
                        <div key={i} className="flex justify-between items-center py-3">
                          <div>
                            <p className="text-sm font-medium uppercase tracking-wide">{s.naziv}</p>
                            <p className="text-xs text-neutral-400 mt-0.5">
                              {s.velicina} · {s.boja} · Kom: {s.kolicina}
                            </p>
                          </div>
                          <p className="text-sm">
                            {(s.kolicina * s.cijena_po_komadu).toLocaleString()} RSD
                          </p>
                        </div>
                      ))}
                    </div>
                    <div className="flex justify-between items-center pt-4 mt-2 border-t border-neutral-300">
                      <span className="text-xs tracking-widest uppercase text-neutral-400">Ukupno</span>
                      <span className="text-base font-medium">
                        {Number(orderDetail.ukupan_iznos).toLocaleString()} RSD
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ── Tab: Adrese ── */}
        {tab === 'addresses' && (
          <div>
            {/* Address list */}
            <div className="space-y-3 mb-6">
              {addresses.length === 0 && !showAddForm && (
                <div className="text-center py-12">
                  <p className="text-xs tracking-widest uppercase text-neutral-300 mb-6">
                    Nemate sačuvanih adresa
                  </p>
                </div>
              )}
              {addresses.map(a => (
                <div
                  key={a.adresa_id}
                  className={`flex justify-between items-start p-5 border transition ${
                    a.je_podrazumijevana ? 'border-black' : 'border-neutral-200'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    {a.je_podrazumijevana && (
                      <p className="text-xs tracking-widest uppercase font-medium mb-1.5">
                        ✓ Podrazumevana
                      </p>
                    )}
                    <p className="text-sm font-medium">
                      {a.ulica} {a.kucni_broj}{a.sprat ? `, ${a.sprat}` : ''}
                    </p>
                    <p className="text-xs text-neutral-500 mt-0.5">
                      {a.postanski_broj} {a.grad}, {a.drzava}
                    </p>
                    <p className="text-xs tracking-widest uppercase text-neutral-300 mt-1">
                      {a.tip_adrese}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-4">
                    {!a.je_podrazumijevana && (
                      <button
                        onClick={() => handleSetDefault(a.adresa_id)}
                        className="text-xs tracking-widest uppercase border border-neutral-300 px-3 py-1.5 hover:border-black transition"
                      >
                        Postavi kao default
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteAddress(a.adresa_id)}
                      className="p-1.5 text-neutral-300 hover:text-red-500 hover:bg-red-50 transition"
                      title="Obriši adresu"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Add address button */}
            {!showAddForm && (
              <button
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 text-xs tracking-widest uppercase border border-black px-5 py-3 hover:bg-black hover:text-white transition"
              >
                <Plus size={13} /> DODAJ ADRESU
              </button>
            )}

            {/* Add address form */}
            {showAddForm && (
              <form onSubmit={handleAddAddress} className="border border-neutral-200 p-6 space-y-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xs tracking-widest uppercase font-medium">Nova adresa</h3>
                  <button type="button" onClick={() => setShowAddForm(false)}>
                    <X size={16} className="text-neutral-400 hover:text-black transition" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1">Ulica *</label>
                    <input
                      required
                      className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                      value={newAddr.ulica}
                      onChange={e => setNewAddr({ ...newAddr, ulica: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1">Kućni broj *</label>
                    <input
                      required
                      className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                      value={newAddr.kucni_broj}
                      onChange={e => setNewAddr({ ...newAddr, kucni_broj: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-neutral-400 mb-1">Sprat (opciono)</label>
                  <input
                    className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                    value={newAddr.sprat}
                    onChange={e => setNewAddr({ ...newAddr, sprat: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1">Pošt. broj *</label>
                    <input
                      required
                      className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                      value={newAddr.mesto.postanski_broj}
                      onChange={e => setNewAddr({ ...newAddr, mesto: { ...newAddr.mesto, postanski_broj: e.target.value } })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1">Grad *</label>
                    <input
                      required
                      className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                      value={newAddr.mesto.grad}
                      onChange={e => setNewAddr({ ...newAddr, mesto: { ...newAddr.mesto, grad: e.target.value } })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1">Država *</label>
                    <CountrySelect
                      required
                      value={newAddr.mesto.drzava}
                      onChange={val => setNewAddr({ ...newAddr, mesto: { ...newAddr.mesto, drzava: val } })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-neutral-400 mb-1">Tip adrese</label>
                  <select
                    className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black"
                    value={newAddr.tip_adrese}
                    onChange={e => setNewAddr({ ...newAddr, tip_adrese: e.target.value })}
                  >
                    <option value="kucna">Kućna</option>
                    <option value="poslovna">Poslovna</option>
                  </select>
                </div>

                <label className="flex items-center gap-2.5 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    className="accent-black"
                    checked={newAddr.je_podrazumijevana}
                    onChange={e => setNewAddr({ ...newAddr, je_podrazumijevana: e.target.checked })}
                  />
                  <span className="text-xs tracking-widest uppercase text-neutral-500">
                    Postavi kao podrazumijevanu
                  </span>
                </label>

                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    className="flex-1 bg-black text-white text-xs tracking-widest uppercase py-3 hover:bg-neutral-800 transition"
                  >
                    SAČUVAJ ADRESU
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 border border-neutral-300 text-xs tracking-widest uppercase py-3 hover:border-black transition"
                  >
                    OTKAŽI
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
