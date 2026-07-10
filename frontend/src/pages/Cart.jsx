import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api/axios';
import { Trash2, Minus, Plus } from 'lucide-react';

export default function Cart({ user }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadCart = async () => {
    if (!user) { setLoading(false); return; }
    try {
      const res = await api.get(`/cart/${user.id}`);
      setCart(res.data);
    } catch {
      setCart(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCart(); }, [user]);

  const handleQty = async (stavkaId, newQty) => {
    if (newQty < 1 || newQty > 99) return;
    try {
      await api.put(`/cart/${user.id}/items/${stavkaId}?kolicina=${newQty}`);
      setCart(prev => {
        const stavke = prev.stavke.map(s =>
          s.stavka_id === stavkaId ? { ...s, kolicina: newQty } : s
        );
        return { ...prev, stavke, ukupno: stavke.reduce((sum, s) => sum + s.kolicina * s.cijena_po_komadu, 0) };
      });
    } catch { alert('Greška pri izmjeni količine.'); }
  };

  const handleDelete = async (stavkaId) => {
    try {
      await api.delete(`/cart/${user.id}/items/${stavkaId}`);
      loadCart();
    } catch { alert('Greška pri brisanju stavke.'); }
  };

  if (!user) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <p className="text-sm text-neutral-400">
        <Link to="/login" className="underline">Prijavite se</Link> da vidite korpu.
      </p>
    </div>
  );

  if (loading) return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center">
      <p className="text-xs tracking-widest uppercase text-neutral-300">Učitavanje...</p>
    </div>
  );

  const items = cart?.stavke || [];
  const total = items.reduce((sum, s) => sum + s.kolicina * s.cijena_po_komadu, 0);

  return (
    <div className="min-h-screen bg-white pt-14">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-serif mb-10">Korpa</h1>

        {items.length === 0 ? (
          <div className="text-center py-24 border-t border-neutral-200">
            <p className="text-xs tracking-widest uppercase text-neutral-400 mb-8">Vaša korpa je prazna</p>
            <Link
              to="/kolekcija"
              className="inline-block bg-black text-white text-xs tracking-widest uppercase px-10 py-4 hover:bg-neutral-800 transition"
            >
              NASTAVI KUPOVINU
            </Link>
          </div>
        ) : (
          <>
            {/* Header row */}
            <div className="grid grid-cols-12 text-xs tracking-widest uppercase text-neutral-400 pb-3 border-b border-neutral-200 mb-1">
              <span className="col-span-6">Proizvod</span>
              <span className="col-span-3 text-center">Količina</span>
              <span className="col-span-2 text-right">Cijena</span>
              <span className="col-span-1" />
            </div>

            {/* Items */}
            <div className="divide-y divide-neutral-100">
              {items.map(item => (
                <div key={item.stavka_id} className="grid grid-cols-12 items-center py-5 gap-2">
                  {/* Product info */}
                  <div className="col-span-6">
                    <p className="text-xs font-medium uppercase tracking-wide leading-tight mb-1">
                      {item.naziv}
                    </p>
                    <p className="text-xs text-neutral-400">
                      {item.velicina} · {item.boja}
                    </p>
                    <p className="text-xs text-neutral-500 mt-1">
                      {Number(item.cijena_po_komadu).toLocaleString()} RSD / kom
                    </p>
                  </div>

                  {/* Quantity */}
                  <div className="col-span-3 flex items-center justify-center gap-1">
                    <button
                      onClick={() => handleQty(item.stavka_id, item.kolicina - 1)}
                      disabled={item.kolicina <= 1}
                      className="w-7 h-7 flex items-center justify-center border border-neutral-300 hover:border-black transition disabled:opacity-25"
                    >
                      <Minus size={11} />
                    </button>
                    <span className="w-8 text-center text-sm">{item.kolicina}</span>
                    <button
                      onClick={() => handleQty(item.stavka_id, item.kolicina + 1)}
                      className="w-7 h-7 flex items-center justify-center border border-neutral-300 hover:border-black transition"
                    >
                      <Plus size={11} />
                    </button>
                  </div>

                  {/* Total */}
                  <div className="col-span-2 text-right">
                    <p className="text-sm font-medium">
                      {(item.kolicina * item.cijena_po_komadu).toLocaleString()} RSD
                    </p>
                  </div>

                  {/* Delete */}
                  <div className="col-span-1 flex justify-end">
                    <button
                      onClick={() => handleDelete(item.stavka_id)}
                      className="text-neutral-300 hover:text-black transition p-1"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="border-t border-neutral-200 pt-8 mt-4">
              <div className="flex justify-between items-baseline mb-8">
                <span className="text-xs tracking-widest uppercase text-neutral-400">Ukupno</span>
                <span className="text-2xl font-serif">{total.toLocaleString()} RSD</span>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full bg-black text-white text-xs tracking-widest uppercase py-4 hover:bg-neutral-800 transition mb-4"
              >
                NASTAVI NA PLAĆANJE
              </button>

              <Link
                to="/kolekcija"
                className="block text-center text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition underline"
              >
                NASTAVI KUPOVINU
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
