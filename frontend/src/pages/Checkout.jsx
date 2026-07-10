import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api/axios';
import { MapPin, CheckCircle } from 'lucide-react';

export default function Checkout({ user }) {
  const [addresses, setAddresses] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) { setLoading(false); return; }
    api.get(`/users/${user.id}/adrese`)
      .then(res => {
        const list = res.data || [];
        setAddresses(list);
        const def = list.find(a => a.je_podrazumijevana);
        setSelectedId(def ? def.adresa_id : list[0]?.adresa_id ?? null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  const selectedAddress = addresses.find(a => a.adresa_id === selectedId);

  const formatAddress = (a) =>
    `${a.ulica} ${a.kucni_broj}${a.sprat ? `/${a.sprat}` : ''}, ${a.postanski_broj} ${a.grad}, ${a.drzava}`;

  const handleConfirm = async (e) => {
    e.preventDefault();
    if (!selectedAddress) return;
    setSubmitting(true);
    try {
      await api.post(`/orders/${user.id}`, {
        adresa_isporuke: formatAddress(selectedAddress),
        email: user.email,
        user_name: `${user.ime} ${user.prezime}`,
      });
      setConfirmed(true);
      setTimeout(() => navigate('/'), 3000);
    } catch (err) {
      alert('Greška: ' + (err.response?.data?.detail || 'Pokušajte ponovo.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <p className="text-sm text-neutral-400">
        <Link to="/login" className="underline">Prijavite se</Link> da biste nastavili.
      </p>
    </div>
  );

  if (loading) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <p className="text-xs tracking-widest uppercase text-neutral-300">Učitavanje...</p>
    </div>
  );

  if (confirmed) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <div className="text-center">
        <CheckCircle size={44} className="text-green-500 mx-auto mb-5" />
        <h2 className="text-2xl font-serif mb-2">Narudžbina potvrđena</h2>
        <p className="text-xs text-neutral-400 tracking-widest uppercase">
          Preusmjeravamo vas na početnu stranicu...
        </p>
      </div>
    </div>
  );

  if (addresses.length === 0) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <div className="text-center max-w-sm px-6">
        <MapPin size={36} className="text-neutral-300 mx-auto mb-5" />
        <h2 className="text-2xl font-serif mb-3">Nema sačuvanih adresa</h2>
        <p className="text-xs text-neutral-500 leading-relaxed mb-8">
          Da biste nastavili sa narudžbinom, dodajte adresu dostave na svom profilu i postavite je kao podrazumijevanu.
        </p>
        <Link
          to="/profil"
          className="inline-block bg-black text-white text-xs tracking-widest uppercase px-10 py-4 hover:bg-neutral-800 transition"
        >
          IDI NA PROFIL
        </Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white pt-14">
      <div className="max-w-xl mx-auto px-6 py-12">

        {/* Header */}
        <h1 className="text-4xl font-serif mb-2">Dostava</h1>
        <p className="text-xs tracking-widest uppercase text-neutral-400 mb-10">
          Izaberite adresu isporuke
        </p>

        <form onSubmit={handleConfirm} className="space-y-6">

          {/* Address list */}
          <div className="space-y-2">
            {addresses.map(a => (
              <label
                key={a.adresa_id}
                className={`flex items-start gap-4 p-4 border cursor-pointer transition ${
                  selectedId === a.adresa_id
                    ? 'border-black bg-neutral-50'
                    : 'border-neutral-200 hover:border-neutral-400'
                }`}
              >
                <input
                  type="radio"
                  name="adresa"
                  value={a.adresa_id}
                  checked={selectedId === a.adresa_id}
                  onChange={() => setSelectedId(a.adresa_id)}
                  className="mt-1 accent-black shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-0.5">
                    <p className="text-sm font-medium">
                      {a.ulica} {a.kucni_broj}{a.sprat ? `/${a.sprat}` : ''}
                    </p>
                    {a.je_podrazumijevana && (
                      <span className="text-xs tracking-widest uppercase text-neutral-400 border border-neutral-200 px-1.5 py-0.5 shrink-0">
                        Podrazumijevana
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-neutral-400">
                    {a.postanski_broj} {a.grad}, {a.drzava}
                  </p>
                </div>
              </label>
            ))}
          </div>

          {/* Link to manage addresses */}
          <div className="text-right">
            <Link
              to="/profil"
              className="text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition underline"
            >
              Upravljaj adresama
            </Link>
          </div>

          {/* Selected address summary */}
          {selectedAddress && (
            <div className="bg-neutral-50 border border-neutral-200 p-4">
              <p className="text-xs tracking-widest uppercase text-neutral-400 mb-2">Adresa isporuke</p>
              <p className="text-sm font-medium">{formatAddress(selectedAddress)}</p>
            </div>
          )}

          {/* Confirm button */}
          <button
            type="submit"
            disabled={submitting || !selectedId}
            className="w-full bg-black text-white text-xs tracking-widest uppercase py-4 hover:bg-neutral-800 transition disabled:opacity-50"
          >
            {submitting ? 'OBRADA...' : 'POTVRDI NARUDŽBINU'}
          </button>
        </form>
      </div>
    </div>
  );
}
