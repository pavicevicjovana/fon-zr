import { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

export default function CountrySelect({ value, onChange, required = false }) {
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const searchRef = useRef(null);

  useEffect(() => {
    fetch('https://restcountries.com/v3.1/all?fields=name')
      .then(r => r.json())
      .then(data => {
        const names = data.map(c => c.name.common).sort((a, b) => a.localeCompare(b));
        setCountries(names);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  useEffect(() => {
    if (open && searchRef.current) searchRef.current.focus();
  }, [open]);

  const filtered = countries.filter(c =>
    c.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (country) => {
    onChange(country);
    setSearch('');
    setOpen(false);
  };

  const handleToggle = () => {
    if (!loading && !error) {
      setOpen(prev => !prev);
      if (!open) setSearch('');
    }
  };

  if (error) {
    return (
      <input
        type="text"
        required={required}
        placeholder="Unesite državu..."
        className="w-full border border-neutral-300 px-3 py-2.5 text-sm focus:outline-none focus:border-black transition"
        value={value}
        onChange={e => onChange(e.target.value)}
      />
    );
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={handleToggle}
        className={`w-full border px-3 py-2.5 text-sm text-left flex items-center justify-between transition focus:outline-none ${
          open ? 'border-black' : 'border-neutral-300 hover:border-neutral-400'
        }`}
      >
        <span className={value ? 'text-black' : 'text-neutral-400'}>
          {loading ? 'Učitavanje država...' : value || 'Izaberi državu...'}
        </span>
        <ChevronDown
          size={14}
          className={`text-neutral-400 transition-transform shrink-0 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div className="absolute z-50 top-full left-0 right-0 bg-white border border-neutral-300 border-t-0 shadow-lg flex flex-col max-h-56">
          <div className="p-2 border-b border-neutral-100 shrink-0">
            <input
              ref={searchRef}
              type="text"
              placeholder="Pretraži državu..."
              className="w-full px-2 py-1.5 text-sm border border-neutral-200 focus:outline-none focus:border-black transition"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="overflow-y-auto">
            {filtered.length === 0 ? (
              <p className="text-xs text-neutral-400 p-3 text-center tracking-wide">
                Nema rezultata za "{search}"
              </p>
            ) : (
              filtered.map(country => (
                <button
                  key={country}
                  type="button"
                  onClick={() => handleSelect(country)}
                  className={`w-full text-left px-3 py-2 text-sm transition ${
                    value === country
                      ? 'bg-black text-white'
                      : 'hover:bg-neutral-50'
                  }`}
                >
                  {country}
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {required && (
        <input
          tabIndex={-1}
          style={{ position: 'absolute', opacity: 0, height: 0, width: 0, pointerEvents: 'none' }}
          value={value}
          required
          onChange={() => {}}
          onFocus={() => setOpen(true)}
        />
      )}
    </div>
  );
}
