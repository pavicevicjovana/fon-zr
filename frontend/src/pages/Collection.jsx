import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
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
  const [searchValue, setSearchValue] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchPage = async (skip, currentProducts = []) => {
    const res = await api.get(`/products?skip=${skip}&limit=${PAGE_SIZE}`);
    const data = res.data;
    const combined = skip === 0 ? data : [...currentProducts, ...data];
    setProducts(combined);
    setHasMore(data.length === PAGE_SIZE);
    const cats = ['SVE', ...new Set(combined.map(p => p.category?.toUpperCase()).filter(Boolean))];
    setCategories(cats);
    return combined;
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(searchValue.trim());
    }, 300);

    return () => clearTimeout(timer);
  }, [searchValue]);

  useEffect(() => {
    let cancelled = false;

    const loadProducts = async () => {
      setLoading(true);
      try {
        if (searchQuery) {
          const res = await api.get(`/products/search?q=${encodeURIComponent(searchQuery)}`);
          if (cancelled) return;

          const data = Array.isArray(res.data) ? res.data : [];
          setProducts(data);
          setHasMore(false);
          setPage(0);
          const cats = ['SVE', ...new Set(data.map(p => p.category?.toUpperCase()).filter(Boolean))];
          setCategories(cats);
        } else {
          await fetchPage(0, []);
          if (cancelled) return;
          setPage(0);
        }
      } catch {
        if (!cancelled) {
          setProducts([]);
          setHasMore(false);
          setCategories(['SVE']);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadProducts();

    return () => {
      cancelled = true;
    };
  }, [searchQuery]);

  const handleLoadMore = async () => {
    if (searchQuery) return;

    setLoadingMore(true);
    const nextPage = page + 1;
    try {
      await fetchPage(nextPage * PAGE_SIZE, products);
      setPage(nextPage);
    } catch {}
    finally {
      setLoadingMore(false);
    }
  };

  const handleFilter = (cat) => {
    setActiveCategory(cat);
  };

  const filtered = activeCategory === 'SVE'
    ? products
    : products.filter(p => p.category?.toUpperCase() === activeCategory);

  return (
    <div className="min-h-screen bg-white pt-14">
      <div className="border-b border-neutral-200 px-6 py-8">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h1 className="text-4xl font-serif">Kolekcija</h1>

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
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div className="relative w-full md:max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
            <input
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Pretraži proizvode"
              className="w-full border border-neutral-200 bg-white py-3 pl-10 pr-4 text-sm outline-none focus:border-black"
            />
          </div>

          <p className="text-xs text-neutral-400 tracking-wide uppercase">
            {filtered.length} {filtered.length === 1 ? 'proizvod' : 'proizvoda'}
          </p>
        </div>

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
                <ProductCard key={p.id || p._id} product={p} user={user} />
              ))}
            </div>

            {hasMore && activeCategory === 'SVE' && !searchQuery && (
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
