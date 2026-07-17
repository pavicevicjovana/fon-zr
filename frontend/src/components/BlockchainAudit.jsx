import { useState, useEffect } from 'react';
import { api } from '../api/axios';
import { Link2, ChevronDown, ChevronUp } from 'lucide-react';

/**
 * Prikaz revizijskog traga narudzbine procitanog sa blokcejn mreze.
 *
 * Podaci NE dolaze iz baze podataka, vec se citaju direktno iz pametnog
 * ugovora SagaAudit, preko endpointa /orders/{korisnik_id}/{narudzba_id}/audit.
 *
 * @param {number}  userId    - ID korisnika (potreban zbog provere vlasnistva)
 * @param {number}  orderId   - ID narudzbine
 * @param {boolean} detailed  - prikaz tehnickih detalja (adrese naloga, servisi).
 *                              Koristi se u admin panelu.
 */

// Nazivi koraka su na lancu tehnicki (ORDER_CREATED), a korisniku se
// prikazuju citljivo. Mapiranje je namerno na klijentu: na lanac idu
// stabilni identifikatori, a ne tekst koji se moze menjati.
const NAZIVI_KORAKA = {
  ORDER_CREATED: 'Narudžbina primljena',
  STOCK_RESERVED: 'Zalihe rezervisane',
  STOCK_RESERVATION_FAILED: 'Nema dovoljno zaliha',
  ORDER_CONFIRMED: 'Narudžbina potvrđena',
  ORDER_CANCELLED: 'Narudžbina otkazana',
};

const STIL_STATUSA = {
  SUCCESS: { tacka: 'bg-black', tekst: 'text-neutral-400', oznaka: 'Uspešno' },
  FAILED: { tacka: 'bg-red-600', tekst: 'text-red-600', oznaka: 'Neuspešno' },
  COMPENSATED: { tacka: 'bg-amber-500', tekst: 'text-amber-600', oznaka: 'Kompenzacija' },
};

const skrati = (v, pocetak = 6, kraj = 4) =>
  v && v.length > pocetak + kraj ? `${v.slice(0, pocetak)}…${v.slice(-kraj)}` : v;

const formatirajVreme = (unixSekunde) =>
  new Date(unixSekunde * 1000).toLocaleString('sr-Latn-RS', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });

export default function BlockchainAudit({ userId, orderId, detailed = false }) {
  const [podaci, setPodaci] = useState(null);
  const [ucitavanje, setUcitavanje] = useState(true);
  const [greska, setGreska] = useState(null);
  const [otvoren, setOtvoren] = useState(detailed);

  useEffect(() => {
    let aktivan = true;

    const ucitaj = async () => {
      setUcitavanje(true);
      setGreska(null);
      try {
        const res = await api.get(`/orders/${userId}/${orderId}/audit`);
        if (aktivan) setPodaci(res.data);
      } catch {
        if (aktivan) setGreska('Revizijski trag trenutno nije dostupan.');
      } finally {
        if (aktivan) setUcitavanje(false);
      }
    };

    ucitaj();
    return () => { aktivan = false; };
  }, [userId, orderId]);

  const koraci = podaci?.koraci ?? [];

  return (
    <div className="mt-5 pt-5 border-t border-neutral-300">
      <button
        onClick={() => setOtvoren(!otvoren)}
        className="w-full flex items-center justify-between text-left group"
      >
        <span className="flex items-center gap-2">
          <Link2 size={12} className="text-neutral-400" />
          <span className="text-xs tracking-widest uppercase text-neutral-500 group-hover:text-black transition">
            Zapis na blokčejnu
          </span>
          {!ucitavanje && !greska && (
            <span className="text-xs text-neutral-300">
              {koraci.length} {koraci.length === 1 ? 'korak' : 'koraka'}
            </span>
          )}
        </span>
        {otvoren
          ? <ChevronUp size={14} className="text-neutral-400" />
          : <ChevronDown size={14} className="text-neutral-400" />}
      </button>

      {otvoren && (
        <div className="mt-5">
          {ucitavanje && (
            <p className="text-xs tracking-widest uppercase text-neutral-300">Učitavanje…</p>
          )}

          {greska && (
            <p className="text-xs text-neutral-400">{greska}</p>
          )}

          {!ucitavanje && !greska && koraci.length === 0 && (
            <p className="text-xs text-neutral-400">
              Za ovu narudžbinu još nema zapisa na blokčejnu.
            </p>
          )}

          {!ucitavanje && koraci.length > 0 && (
            <>
              <ol className="relative">
                {/* Vertikalna linija koja povezuje korake */}
                <div className="absolute left-[3px] top-2 bottom-2 w-px bg-neutral-200" />

                {koraci.map((k, i) => {
                  const stil = STIL_STATUSA[k.status] ?? STIL_STATUSA.SUCCESS;
                  return (
                    <li key={i} className="relative pl-6 pb-5 last:pb-0">
                      {/* Kvadratni marker - bez zaobljenja, u duhu ostatka sajta */}
                      <span className={`absolute left-0 top-1.5 w-[7px] h-[7px] ${stil.tacka}`} />

                      <p className="text-sm font-medium">
                        {NAZIVI_KORAKA[k.step_name] ?? k.step_name}
                      </p>

                      <p className="text-xs text-neutral-400 mt-0.5">
                        {formatirajVreme(k.timestamp)}
                        {' · '}
                        <span className={`uppercase tracking-wide ${stil.tekst}`}>
                          {stil.oznaka}
                        </span>
                      </p>

                      {detailed && (
                        <div className="mt-1.5 space-y-0.5">
                          <p className="text-xs text-neutral-400">
                            <span className="tracking-widest uppercase text-neutral-300">Servis: </span>
                            {k.service_name}
                          </p>
                          <p className="text-xs text-neutral-400">
                            <span className="tracking-widest uppercase text-neutral-300">Potpisao: </span>
                            <span className="font-mono" title={k.recorded_by}>
                              {skrati(k.recorded_by, 10, 8)}
                            </span>
                          </p>
                          <p className="text-xs text-neutral-400">
                            <span className="tracking-widest uppercase text-neutral-300">Oznaka koraka: </span>
                            <span className="font-mono">{k.step_name}</span>
                          </p>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ol>

              <p className="text-xs text-neutral-400 mt-5 pt-4 border-t border-neutral-200 leading-relaxed">
                Ovi koraci su pročitani sa blokčejn mreže, a ne iz baze podataka.
                Svaki korak potpisao je servis koji ga je izvršio i naknadno se ne može izmeniti.
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}