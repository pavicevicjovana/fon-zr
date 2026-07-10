import { useState } from 'react';
import { api } from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Login({ setUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/users/login', { email, lozinka: password });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.korisnik));
      setUser(res.data.korisnik);
      navigate(res.data.korisnik.rola === 'administrator' ? '/panel' : '/');
    } catch {
      alert('Pogrešan email ili lozinka.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white pt-14 flex items-center justify-center px-6">
      <div className="w-full max-w-sm py-12">
        <h1 className="text-4xl font-serif text-center mb-2">Prijava</h1>
        <p className="text-xs text-neutral-400 text-center tracking-widest uppercase mb-10">
          Ulogujte se na vaš nalog
        </p>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">
              Email
            </label>
            <input
              type="email"
              required
              autoComplete="email"
              className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs tracking-widest uppercase text-neutral-500 mb-1.5">
              Lozinka
            </label>
            <input
              type="password"
              required
              autoComplete="current-password"
              className="w-full border border-neutral-300 px-4 py-3 text-sm focus:outline-none focus:border-black transition"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-black text-white text-xs tracking-widest uppercase py-4 hover:bg-neutral-800 transition disabled:opacity-50 mt-2"
          >
            {loading ? 'PRIJAVLJIVANJE...' : 'PRIJAVI SE'}
          </button>
        </form>

        <p className="mt-8 text-center text-xs text-neutral-400">
          Nemate nalog?{' '}
          <Link to="/register" className="text-black underline hover:opacity-60 transition">
            Registrujte se
          </Link>
        </p>
      </div>
    </div>
  );
}
