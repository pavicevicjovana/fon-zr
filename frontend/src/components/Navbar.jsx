import { Link } from 'react-router-dom';
import { ShoppingBag, User, ShieldCheck } from 'lucide-react';

export default function Navbar({ user, logout }) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-neutral-200">
      <div className="max-w-screen-xl mx-auto px-6 h-14 flex items-center">
        {/* Left: links */}
        <div className="flex items-center gap-8 flex-1">
          <Link to="/kolekcija" className="text-xs tracking-widest uppercase hover:opacity-50 transition hidden md:block">
            Kolekcija
          </Link>
          {user?.rola === 'administrator' && (
            <Link to="/panel" className="text-xs tracking-widest uppercase text-neutral-400 hover:opacity-50 transition flex items-center gap-1 hidden md:block">
              <ShieldCheck size={13} className="inline mr-1" />Admin
            </Link>
          )}
        </div>

        {/* Center: logo */}
        <Link to="/" className="text-xl font-bold tracking-[0.4em] uppercase absolute left-1/2 -translate-x-1/2">
          VELURA
        </Link>

        {/* Right: icons */}
        <div className="flex items-center gap-5 flex-1 justify-end">
          {user ? (
            <>
              <Link
                to="/profil"
                className="text-xs tracking-widest uppercase hover:opacity-50 transition hidden md:flex items-center gap-1.5"
              >
                <User size={14} />
                {user.ime}
              </Link>
              <Link to="/profil" className="md:hidden">
                <User size={20} className="hover:opacity-50 transition" />
              </Link>
              <button
                onClick={logout}
                className="text-xs tracking-widest uppercase hover:opacity-50 transition hidden md:block"
              >
                Odjava
              </button>
            </>
          ) : (
            <Link to="/login" className="text-xs tracking-widest uppercase hover:opacity-50 transition">
              Prijava
            </Link>
          )}
          <Link to="/cart">
            <ShoppingBag size={20} className="hover:opacity-50 transition" />
          </Link>
        </div>
      </div>
    </nav>
  );
}
