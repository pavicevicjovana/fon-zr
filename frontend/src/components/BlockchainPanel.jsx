import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import { Link2, Boxes, AlertTriangle, RotateCcw, RefreshCw } from 'lucide-react';

/**
 * Administratorski prikaz stanja blokcejn mreze i statistike revizijskog traga.
 *
 * Svi podaci se citaju sa lanca: javne promenljive ugovora (totalSteps, owner)
 * i StepLogged dogadjaji. Dogadjaji su jedini nacin da se dodje do svih
 * narudzbina, posto ugovor namerno ne cuva njihov spisak - to bi bilo skupo.
 */

const NAZIVI_KORAKA = {
  ORDER_CREATED: 'Narudžbina primljena',
  STOCK_RESERVED: 'Zalihe rezervisane',
  STOCK_RESERVATION_FAILED: 'Nema dovoljno zaliha',
  ORDER_CONFIRMED: 'Narudžbina potvrđena',
  ORDER_CANCELLED: 'Narudžbina otkazana',
};

const STIL_STATUSA = {
  SUCCESS: { klasa: 'bg-green-50 text-green-700', tacka: 'bg-green-500', oznaka: 'Uspešno' },
  FAILED: { klasa: 'bg-red-50 text-red-600', tacka: 'bg-red-500', oznaka: 'Neuspešno' },
  COMPENSATED: { klasa: 'bg-amber-50 text-amber-700', tacka: 'bg-amber-500', oznaka: 'Kompenzacija' },
};

const skrati = (v, p = 10, k = 8) =>
  v && v.length > p + k ? `${v.slice(0, p)}…${v.slice(-k)}` : v;

const vreme = (t) =>
  new Date(t * 1000).toLocaleString('sr-Latn-RS', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
  });

function Kartica({ icon: Icon, label, value, sub, boja = 'black' }) {
  const bojaTeksta =
    boja === 'amber' ? 'text-amber-600' : boja === 'red' ? 'text-red-500' : 'text-black';
  return (
    <div className="bg-white border border-neutral-200 p-5">
      <div className="flex items-start justify-between mb-3">
        <Icon size={18} className="text-neutral-400" />
        <span className={`text-2xl font-serif font-bold ${bojaTeksta}`}>{value}</span>
      </div>
      <p className="text-xs tracking-widest uppercase text-neutral-500">{label}</p>
      {sub && <p className="text-xs text-neutral-300 mt-0.5">{sub}</p>}
    </div>
  );
}

function Red({ label, children }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-neutral-100 last:border-0">
      <span className="text-xs tracking-widest uppercase text-neutral-400">{label}</span>
      <span className="text-xs">{children}</span>
    </div>
  );
}

export default function BlockchainPanel({ onLoaded }) {
  const [podaci, setPodaci] = useState(null);
  const [ucitavanje, setUcitavanje] = useState(true);

  const ucitaj = async () => {
    setUcitavanje(true);
    try {
      const res = await api.get('/admin/blockchain');
      setPodaci(res.data);
      onLoaded?.(res.data);
    } catch {
      setPodaci({ povezan: false, razlog: 'Servis nije dostupan.' });
    } finally {
      setUcitavanje(false);
    }
  };

  useEffect(() => { ucitaj(); }, []);

  if (ucitavanje) {
    return (
      <div className="text-center py-16 text-xs text-neutral-300 uppercase tracking-widest">
        Učitavanje…
      </div>
    );
  }

  if (!podaci?.povezan) {
    return (
      <div className="text-center py-16">
        <AlertTriangle size={28} className="text-neutral-300 mx-auto mb-3" />
        <p className="text-xs tracking-widest uppercase text-neutral-400 mb-1">
          Blokčejn mreža nije dostupna
        </p>
        <p className="text-xs text-neutral-300">{podaci?.razlog}</p>
        <button
          onClick={ucitaj}
          className="mt-5 inline-flex items-center gap-1.5 text-xs border border-neutral-300 px-4 py-2 hover:border-black transition"
        >
          <RefreshCw size={12} /> Pokušaj ponovo
        </button>
      </div>
    );
  }

  const { mreza, ugovor, statistika, poslednji_koraci } = podaci;

  return (
    <div className="p-5 space-y-6">

      {/* Statistika revizijskog traga */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Kartica
          icon={Link2}
          label="Koraka na lancu"
          value={ugovor.ukupno_koraka}
          sub={`u ${mreza.broj_blokova} blokova`}
        />
        <Kartica
          icon={Boxes}
          label="Narudžbina sa zapisom"
          value={statistika.narudzbina_sa_zapisom}
        />
        <Kartica
          icon={RotateCcw}
          label="Kompenzovanih saga"
          value={statistika.kompenzovanih_saga}
          boja="amber"
        />
        <Kartica
          icon={AlertTriangle}
          label="Neuspelih koraka"
          value={statistika.po_statusu.FAILED ?? 0}
          boja="red"
        />
      </div>

      {/* Mreza i ugovor */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-neutral-200 p-5">
          <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400 mb-3">
            Mreža
          </p>
          <Red label="Čvor">
            <span className="font-mono text-neutral-500">{mreza.rpc}</span>
          </Red>
          <Red label="Chain ID">
            <span className="font-mono">{mreza.chain_id}</span>
          </Red>
          <Red label="Broj blokova">
            <span className="font-mono">{mreza.broj_blokova}</span>
          </Red>
          <Red label="Status">
            <span className="inline-flex items-center gap-1.5 text-green-700">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> Povezan
            </span>
          </Red>
        </div>

        <div className="bg-white border border-neutral-200 p-5">
          <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400 mb-3">
            Pametni ugovor SagaAudit
          </p>
          <Red label="Adresa">
            <span className="font-mono" title={ugovor.adresa}>{skrati(ugovor.adresa)}</span>
          </Red>
          <Red label="Vlasnik">
            <span className="font-mono text-neutral-500" title={ugovor.vlasnik}>
              {skrati(ugovor.vlasnik)}
            </span>
          </Red>
          <Red label="Upisano koraka">
            <span className="font-mono">{ugovor.ukupno_koraka}</span>
          </Red>
        </div>
      </div>

      {/* Ko pise na lanac */}
      <div className="bg-white border border-neutral-200 p-5">
        <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400 mb-3">
          Upisi po servisu
        </p>
        <div className="space-y-2">
          {Object.entries(statistika.po_servisu).map(([servis, broj]) => {
            const procenat = Math.round((broj / ugovor.ukupno_koraka) * 100);
            return (
              <div key={servis}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium">{servis}</span>
                  <span className="text-neutral-400">{broj} · {procenat}%</span>
                </div>
                <div className="h-1 bg-neutral-100">
                  <div className="h-1 bg-black" style={{ width: `${procenat}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Poslednji koraci */}
      <div className="bg-white border border-neutral-200">
        <div className="flex items-center justify-between px-5 py-3 border-b border-neutral-200">
          <p className="text-xs font-semibold tracking-widest uppercase text-neutral-400">
            Poslednji upisi
          </p>
          <button
            onClick={ucitaj}
            className="inline-flex items-center gap-1.5 text-xs text-neutral-400 hover:text-black transition"
          >
            <RefreshCw size={12} /> Osveži
          </button>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 text-left">
              {['Narudžbina', 'Korak', 'Status', 'Servis', 'Blok', 'Transakcija', 'Vreme'].map(h => (
                <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {poslednji_koraci.map((k, i) => {
              const stil = STIL_STATUSA[k.status] ?? STIL_STATUSA.SUCCESS;
              return (
                <tr key={i} className="hover:bg-neutral-50 transition">
                  <td className="px-4 py-3 text-xs font-mono text-neutral-400">#{k.narudzba_id}</td>
                  <td className="px-4 py-3">
                    <p className="text-xs font-medium">{NAZIVI_KORAKA[k.step_name] ?? k.step_name}</p>
                    <p className="text-xs text-neutral-300 font-mono mt-0.5">{k.step_name}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 ${stil.klasa}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${stil.tacka}`} />
                      {stil.oznaka}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-neutral-500">{k.service_name}</td>
                  <td className="px-4 py-3 text-xs font-mono text-neutral-400">{k.blok}</td>
                  <td className="px-4 py-3 text-xs font-mono text-neutral-300" title={k.tx_hash}>
                    {skrati(k.tx_hash, 8, 6)}
                  </td>
                  <td className="px-4 py-3 text-xs text-neutral-400 whitespace-nowrap">
                    {vreme(k.timestamp)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-neutral-400 leading-relaxed">
        Podaci se čitaju sa blokčejn mreže, iz pametnog ugovora i njegovih događaja.
        Ugovor namerno ne čuva spisak narudžbina jer bi to bilo skupo za upis, pa se
        pregled svih koraka dobija pretragom StepLogged događaja.
      </p>
    </div>
  );
}