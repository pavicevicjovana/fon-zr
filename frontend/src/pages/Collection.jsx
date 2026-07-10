import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import ProductCard from '../components/ProductCard';

const PAGE_SIZE = 12;

export default function Collection({ user }) {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState(['SVE']);
  const [activeCategory, setActiveCategory] = useState('SVE');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const fetchPage = async (skip, category, currentProducts) => {
    const res = await api.get(`/products?skip=${skip}&limit=${PAGE_SIZE}`);
    const data = res.data;
    const combined = skip === 0 ? data : [...currentProducts, ...data];
    setProducts(combined);
    setHasMore(data.length === PAGE_SIZE);
    const cats = ['SVE', ...new Set(combined.map(p => p.category.toUpperCase()))];
    setCategories(cats);
    return combined;
  };

  useEffect(() => {
    setLoading(true);
    fetchPage(0, 'SVE', [])
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleLoadMore = async () => {
    setLoadingMore(true);
    const nextPage = page + 1;
    try {
      await fetchPage(nextPage * PAGE_SIZE, activeCategory, products);
      setPage(nextPage);
    } catch {}
    finally { setLoadingMore(false); }
  };

  const handleFilter = (cat) => {
    setActiveCategory(cat);
  };

  const filtered = activeCategory === 'SVE'
    ? products
    : products.filter(p => p.category.toUpperCase() === activeCategory);

  return (
    <div className="min-h-screen bg-white pt-14">
      {/* Page header */}
      <div className="border-b border-neutral-200 px-6 py-8">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h1 className="text-4xl font-serif">Kolekcija</h1>

          {/* Category filter */}
          <div className="flex items-center gap-6 flex-wrap">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => handleFilter(cat)}
                className={`text-xs tracking-widest uppercase pb-0.5 transition ${
                  activeCategory === cat
                    ? 'border-b border-black text-black'
                    : 'text-neutral-400 hover:text-black'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 py-10">
        <p className="text-xs text-neutral-400 tracking-wide mb-8 uppercase">
          {filtered.length} {filtered.length === 1 ? 'proizvod' : 'proizvoda'}
        </p>

        {loading ? (
          <div className="text-center py-32 text-xs tracking-widest uppercase text-neutral-300">
            Učitavanje...
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-32 text-xs tracking-widest uppercase text-neutral-300">
            Nema proizvoda
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-14">
              {filtered.map(p => (
                <ProductCard key={p.id} product={p} user={user} />
              ))}
            </div>

            {hasMore && activeCategory === 'SVE' && (
              <div className="text-center mt-16">
                <button
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="border border-black text-xs tracking-widest uppercase px-12 py-4 hover:bg-black hover:text-white transition disabled:opacity-50"
                >
                  {loadingMore ? 'UČITAVANJE...' : 'UČITAJ VIŠE'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
