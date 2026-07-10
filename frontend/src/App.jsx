import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Register from './pages/Register';
import Collection from './pages/Collection';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Profile from './pages/Profile';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const saved = localStorage.getItem('user');
    if (saved) setUser(JSON.parse(saved));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="bg-white min-h-screen">
        <Navbar user={user} logout={handleLogout} />
        <main>
          <Routes>
            <Route path="/" element={<Home user={user} />} />
            <Route path="/panel" element={<Admin user={user} />} />
            <Route path="/login" element={<Login setUser={setUser} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/cart" element={<Cart user={user} />} />
            <Route path="/checkout" element={<Checkout user={user} />} />
            <Route path="/kolekcija" element={<Collection user={user} />} />
            <Route path="/profil" element={<Profile user={user} setUser={setUser} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;
