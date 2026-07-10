import { useState, useMemo } from 'react';
import { api } from '../api/axios';

const colorMap = {
  'bijela': '#FFFFFF',
  'bela': '#FFFFFF',
  'crna': '#1C1C1C',
  'roza': '#F4A7B4',
  'roze': '#F4A7B4',
  'crvena': '#E53935',
  'plava': '#4169E1',
  'svetlo plava': '#87CEEB',
  'tamno plava': '#0D1B4B',
  'teget': '#1A237E',
  'siva': '#9E9E9E',
  'svetlo siva': '#D9D9D9',
  'tamno siva': '#424242',
  'smeđa': '#795548',
  'smeda': '#795548',
  'bež': '#F5F0E8',
  'bez': '#F5F0E8',
  'krem': '#FFF8E7',
  'zelena': '#4CAF50',
  'maslinasta': '#6B7C3D',
  'narančasta': '#FF9800',
  'narandzasta': '#FF9800',
  'bordo': '#6D1A36',
  'ljubičasta': '#9C27B0',
  'ljubicasta': '#9C27B0',
  'žuta': '#FDD835',
  'zuta': '#FDD835',
  'tirkizna': '#00BCD4',
  'srebrna': '#C0C0C0',
  'zlatna': '#FFD700',
  'kajsija': '#F4A460',
};

const productImageMap = [
  { keywords: ['haljina'], url: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80' },
  { keywords: ['suknja'], url: 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=600&q=80' },
  { keywords: ['majica', 't-shirt', 'tshirt'], url: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80' },
  { keywords: ['polo'], url: 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=600&q=80' },
  { keywords: ['košulja', 'kosulja'], url: 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&q=80' },
  { keywords: ['duks', 'hoodie', 'dukserica'], url: 'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80' },
  { keywords: ['džemper', 'dzemper', 'džemper'], url: 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80' },
  { keywords: ['zimska jakna', 'zimska'], url: 'https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&q=80' },
  { keywords: ['kožna jakna', 'kozna jakna', 'biker'], url: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80' },
  { keywords: ['vetrovka', 'wiatrówka'], url: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&q=80' },
  { keywords: ['jakna', 'kaput', 'mantil'], url: 'https://images.unsplash.com/photo-1548126032-079a0fb0099d?w=600&q=80' },
  { keywords: ['trenerka', 'jogger', 'trening'], url: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80' },
  { keywords: ['šorts', 'sorts', 'bermude'], url: 'https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=600&q=80' },
  { keywords: ['farmerke', 'jeans', 'džins', 'dzins'], url: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80' },
  { keywords: ['chino', 'pantalone', 'hlače'], url: 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80' },
  { keywords: ['patike', 'sneaker', 'tenisice'], url: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80' },
  { keywords: ['cipele', 'oksfordice', 'loafer'], url: 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&q=80' },
  { keywords: ['čizme', 'cizme', 'boots'], url: 'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&q=80' },
  { keywords: ['sandale', 'flip'], url: 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&q=80' },
  { keywords: ['baletanke', 'balerinke', 'ballet'], url: 'https://images.unsplash.com/photo-1571601803793-e05de344f082?w=600&q=80' },
  { keywords: ['torba', 'tašna', 'tasna', 'bag'], url: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80' },
  { keywords: ['kaiš', 'kais', 'remen'], url: 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&q=80' },
  { keywords: ['kapa', 'šešir', 'sesir', 'hat'], url: 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=600&q=80' },
  { keywords: ['šal', 'sal', 'marama'], url: 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=600&q=80' },
  { keywords: ['rukavice'], url: 'https://images.unsplash.com/photo-1545594861-3bef43ff2fc8?w=600&q=80' },
  { keywords: ['nakit', 'ogrlica', 'narukvica', 'prsten'], url: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&q=80' },
  { keywords: ['sunčane naočare', 'naocare', 'naočare'], url: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80' },
];

const categoryFallback = {
  odeca: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&q=80',
  obuca: 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=600&q=80',
  dodaci: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80',
};

function getProductImage(name, category) {
  const lower = (name || '').toLowerCase();
  for (const entry of productImageMap) {
    if (entry.keywords.some(kw => lower.includes(kw))) return entry.url;
  }
  return categoryFallback[(category || '').toLowerCase().trim()] || categoryFallback.odeca;
}

export default function ProductCard({ product, user }) {
  const variants = product.variants || [];

  const uniqueColors = useMemo(
    () => [...new Set(variants.map(v => v.color))],
    [variants]
  );

  const [selectedColor, setSelectedColor] = useState(uniqueColors[0] || null);
  const [selectedSize, setSelectedSize] = useState(null);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const availableSizes = useMemo(
    () => variants.filter(v => v.color === selectedColor && v.stock > 0).map(v => v.size),
    [selectedColor, variants]
  );

  const imageUrl = getProductImage(product.name, product.category);

  const handleColorSelect = (color) => {
    setSelectedColor(color);
    setSelectedSize(null);
  };

  const handleAddToCart = async () => {
    if (!user) {
      alert('Morate biti ulogovani da biste dodali proizvod u korpu!');
      return;
    }
    if (!selectedColor || !selectedSize) return;

    setAdding(true);
    try {
      await api.post(`/cart/${user.id}/items`, {
        proizvod_id: product.id || product._id,
        naziv_proizvoda: product.name,
        velicina: selectedSize,
        boja: selectedColor,
        kolicina: 1,
        cijena_po_komadu: parseFloat(product.price),
      });
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch {
      alert('Greška pri dodavanju u korpu.');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="group">
      {/* Image */}
      <div className="relative overflow-hidden bg-neutral-100 aspect-[3/4] mb-3">
        <img
          src={imageUrl}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
        />
        {product.collection && (
          <span className="absolute top-3 left-3 bg-white text-xs tracking-widest uppercase px-2 py-1">
            {product.collection}
          </span>
        )}
      </div>

      {/* Color swatches */}
      {uniqueColors.length > 0 && (
        <div className="flex gap-1.5 mb-2">
          {uniqueColors.map(color => {
            const css = colorMap[color.toLowerCase()] || '#CCC';
            const isWhite = color.toLowerCase() === 'bijela';
            return (
              <button
                key={color}
                title={color}
                onClick={() => handleColorSelect(color)}
                className={`w-4 h-4 rounded-full transition-all ${
                  selectedColor === color
                    ? 'ring-1 ring-offset-1 ring-black scale-110'
                    : 'hover:scale-110'
                } ${isWhite ? 'border border-neutral-300' : ''}`}
                style={{ backgroundColor: css }}
              />
            );
          })}
        </div>
      )}

      {/* Name & price */}
      <p className="text-xs font-medium uppercase tracking-wider text-black mb-0.5 leading-tight">
        {product.name}
      </p>
      <p className="text-xs text-neutral-500 mb-2">
        {Number(product.price).toLocaleString()} RSD
      </p>

      {/* Sizes */}
      {availableSizes.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {availableSizes.map(size => (
            <button
              key={size}
              onClick={() => setSelectedSize(size)}
              className={`text-xs px-2 py-0.5 border transition ${
                selectedSize === size
                  ? 'bg-black text-white border-black'
                  : 'bg-white text-black border-neutral-300 hover:border-black'
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      )}

      {/* Add to cart */}
      <button
        onClick={handleAddToCart}
        disabled={adding || !selectedSize}
        className={`w-full text-xs tracking-widest uppercase py-2 border transition ${
          added
            ? 'bg-neutral-700 text-white border-neutral-700'
            : selectedSize
            ? 'bg-black text-white border-black hover:bg-neutral-800'
            : 'bg-white text-neutral-300 border-neutral-200 cursor-default'
        }`}
      >
        {adding ? 'DODAVANJE...' : added ? 'DODATO ✓' : selectedSize ? 'DODAJ U KORPU' : 'IZABERI VELIČINU'}
      </button>
    </div>
  );
}
