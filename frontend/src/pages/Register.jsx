import { useState } from 'react';
import { api } from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [formData, setFormData] = useState({ email: '', password: '', ime: '', prezime: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/users/register', {
        email: formData.email,
        lozinka: formData.password,
        ime: formData.ime,
        prezime: formData.prezime,
      });
      navigate('/login');
    } catch {
      alert('Greška pri registraciji. Možda email već postoji.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center px-6">
      <div className="w-full max-w-sm py-12">
        <h1 className="text-4xl font-serif text-center mb-2">Registracija</h1>
        <p className="text-xs text-neutral-400 text-center tracking-widest uppercase mb-10">
          Kreirajte nalog
        </p>

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">Ime</label>
              <input
                required
                className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
                onChange={e => setFormData({ ...formData, ime: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">Prezime</label>
              <input
                required
                className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
                onChange={e => setFormData({ ...formData, prezime: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">Email</label>
            <input
              type="email"
              required
              className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
              onChange={e => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">
              Lozinka (min. 8 karaktera)
            </label>
            <input
              type="password"
              required
              minLength={8}
              className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
              onChange={e => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-black text-white text-xs tracking-widest uppercase py-4 hover:bg-neutral-800 transition disabled:opacity-50 mt-2"
          >
            {loading ? 'KREIRANJE NALOGA...' : 'KREIRAJ NALOG'}
          </button>
        </form>

        <p className="mt-8 text-center text-xs text-neutral-400">
          Već imate nalog?{' '}
          <Link to="/login" className="text-black underline hover:opacity-60 transition">
            Prijavite se
          </Link>
        </p>
      </div>
    </div>
  );
}
