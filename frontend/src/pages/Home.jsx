import { useEffect, useState } from 'react';
import { api } from '../api/axios';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';

export default function Home({ user }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/products')
      .then(res => { setProducts(res.data.slice(0, 4)); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-white pt-14">
      {/* Hero */}
      <div className="relative h-[90vh] overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1445205170230-053b83016050?w=1600&q=80"
          alt="Hero"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/30" />
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-20 text-center px-6">
          <p className="text-xs tracking-[0.5em] uppercase text-white/80 mb-5">
            Nova kolekcija 2025
          </p>
          <h1 className="text-7xl md:text-[10rem] font-serif text-white tracking-tight leading-none mb-10">
            VELURA
          </h1>
          <Link
            to="/kolekcija"
            className="bg-white text-black text-xs tracking-widest uppercase px-12 py-4 hover:bg-black hover:text-white transition"
          >
            OTKRIJTE KOLEKCIJU
          </Link>
        </div>
      </div>

      {/* Featured */}
      <section className="max-w-screen-xl mx-auto px-6 py-20">
        <div className="flex justify-between items-baseline mb-10">
          <h2 className="text-3xl font-serif">Izdvojeno</h2>
          <Link
            to="/kolekcija"
            className="text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition"
          >
            Pogledaj sve →
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-20 text-xs tracking-widest uppercase text-neutral-300">
            Učitavanje...
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-x-6 gap-y-12">
            {products.map(p => (
              <ProductCard key={p.id} product={p} user={user} />
            ))}
          </div>
        )}
      </section>

      {/* Editorial banners */}
      <section className="py-6 px-6">
        <div className="max-w-screen-xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="relative overflow-hidden h-[70vh]">
            <img
              src="https://images.unsplash.com/photo-1509631179647-0177331693ae?w=900&q=80"
              alt="Kolekcija"
              className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
            />
            <div className="absolute inset-0 bg-black/10" />
            <div className="absolute bottom-8 left-8">
              <p className="text-xs tracking-widest uppercase text-white/80 mb-2">Proljeće / Ljeto</p>
              <Link
                to="/kolekcija"
                className="inline-block bg-white text-black text-xs tracking-widest uppercase px-8 py-3 hover:bg-black hover:text-white transition"
              >
                ŽENSKA LINIJA
              </Link>
            </div>
          </div>
          <div className="relative overflow-hidden h-[70vh]">
            <img
              src="https://images.unsplash.com/photo-1516826957135-700dedea698c?w=900&q=80"
              alt="Kolekcija"
              className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
            />
            <div className="absolute inset-0 bg-black/10" />
            <div className="absolute bottom-8 left-8">
              <p className="text-xs tracking-widest uppercase text-white/80 mb-2">Jesen / Zima</p>
              <Link
                to="/kolekcija"
                className="inline-block bg-white text-black text-xs tracking-widest uppercase px-8 py-3 hover:bg-black hover:text-white transition"
              >
                MUŠKA LINIJA
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer strip */}
      <div className="border-t border-neutral-200 mt-20 py-10 text-center">
        <p className="text-xs tracking-widest uppercase text-neutral-400">
          © 2025 VELURA · Sve rezervisano
        </p>
      </div>
    </div>
  );
}
