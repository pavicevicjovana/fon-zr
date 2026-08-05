import os
import json
import asyncio
import logging

from web3 import Web3


logger = logging.getLogger(__name__)

STATUS_SUCCESS = 0
STATUS_FAILED = 1
STATUS_COMPENSATED = 2

PRAZAN_HES = b"\x00" * 32


class BlockchainClient:
    def __init__(self, private_key_env: str, service_name: str):
        
        self.service_name = service_name
        self.enabled = False
        self._lock = asyncio.Lock()
        self._tasks = set() 

        rpc_url = os.getenv("BLOCKCHAIN_RPC_URL")
        contract_address = os.getenv("CONTRACT_ADDRESS")
        private_key = os.getenv(private_key_env)
        abi_path = os.getenv("CONTRACT_ABI_PATH", "/app/abi/SagaAudit.json")

        if not (rpc_url and contract_address and private_key):
            logger.warning(
                "Blokcejn klijent nije konfigurisan (%s) - upis koraka je iskljucen.",
                service_name,
            )
            return

        try:
            with open(abi_path, "r", encoding="utf-8") as f:
                abi = json.load(f)

            self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
            self.account = self.w3.eth.account.from_key(private_key)

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi,
            )

            self.enabled = True
            logger.info(
                "Blokcejn klijent spreman (%s): nalog=%s, ugovor=%s",
                service_name, self.account.address, contract_address,
            )
        except Exception as e:
            logger.error("Greska pri inicijalizaciji blokcejn klijenta: %s", e)

    def _posalji_transakciju(self, order_id, step_name, status, correlation_id, payload_hash):
        
        nonce = self.w3.eth.get_transaction_count(self.account.address)

        tx = self.contract.functions.logStep(
            order_id,
            step_name,
            status,
            self.service_name,
            correlation_id or "",
            payload_hash or PRAZAN_HES,
        ).build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gas": 500_000,                   
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)

        raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction")

        tx_hash = self.w3.eth.send_raw_transaction(raw)
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        return tx_hash.hex()

    async def log_step(self, order_id: int, step_name: str, status: int,
                       correlation_id: str = "", payload_hash: bytes = None):
      
        if not self.enabled:
            return None

        try:
        
            async with self._lock:
                tx_hash = await asyncio.to_thread(
                    self._posalji_transakciju,
                    order_id, step_name, status, correlation_id, payload_hash,
                )
            logger.info(
                "Korak %s upisan na blokcejn (narudzbina %s), tx=%s",
                step_name, order_id, tx_hash,
            )
            return tx_hash
        except Exception as e:
            logger.error(
                "Neuspeo upis koraka %s za narudzbinu %s: %s",
                step_name, order_id, e,
            )
            return None

    def log_step_bg(self, order_id: int, step_name: str, status: int,
                    correlation_id: str = "", payload_hash: bytes = None):
        """
        Pokrece upis u pozadini i odmah vraca kontrolu.
        Ovo je metod koji se poziva iz poslovne logike.
        """
        if not self.enabled:
            return
        task = asyncio.create_task(
            self.log_step(order_id, step_name, status, correlation_id, payload_hash)
        )
       
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def _procitaj_korake(self, order_id):

        koraci = self.contract.functions.getSteps(order_id).call()

        nazivi_statusa = {0: "SUCCESS", 1: "FAILED", 2: "COMPENSATED"}
        rezultat = []
        for k in koraci:
            rezultat.append({
                "step_name": k[0],
                "status": nazivi_statusa.get(k[1], str(k[1])),
                "service_name": k[2],
                "correlation_id": k[3],
                "payload_hash": "0x" + k[4].hex(),
                "timestamp": k[5],
                "recorded_by": k[6],
            })
        return rezultat

    async def get_steps(self, order_id: int):
        
        if not self.enabled:
            return []
        try:
            return await asyncio.to_thread(self._procitaj_korake, order_id)
        except Exception as e:
            logger.error("Neuspelo citanje traga za narudzbinu %s: %s", order_id, e)
            return []
        
    def _procitaj_statistiku(self):
        """Sinhroni deo - cita stanje mreze i sve StepLogged dogadjaje."""
        w3 = self.w3

        # Citanje javnih promenljivih ugovora (view pozivi, bez gasa).
        ukupno_koraka = self.contract.functions.totalSteps().call()
        vlasnik = self.contract.functions.owner().call()

        # Citanje SVIH dogadjaja od pocetka lanca. Dogadjaji su jeftiniji od
        # storage-a i mogu se pretrazivati spolja - zato je ovo jedini nacin
        # da se dodje do svih narudzbina, posto ugovor ne cuva njihov spisak.
        try:
            logovi = self.contract.events.StepLogged().get_logs(from_block=0)
        except TypeError:
            # Stariji naziv parametra u web3.py verziji 6.
            logovi = self.contract.events.StepLogged().get_logs(fromBlock=0)

        nazivi_statusa = {0: "SUCCESS", 1: "FAILED", 2: "COMPENSATED"}
        po_statusu = {"SUCCESS": 0, "FAILED": 0, "COMPENSATED": 0}
        po_servisu = {}
        narudzbine = set()
        kompenzovane = set()
        koraci = []

        for log in logovi:
            a = log["args"]
            status = nazivi_statusa.get(a["status"], str(a["status"]))

            po_statusu[status] = po_statusu.get(status, 0) + 1
            po_servisu[a["serviceName"]] = po_servisu.get(a["serviceName"], 0) + 1
            narudzbine.add(a["orderId"])
            if status == "COMPENSATED":
                kompenzovane.add(a["orderId"])

            koraci.append({
                "narudzba_id": a["orderId"],
                "step_name": a["stepName"],
                "status": status,
                "service_name": a["serviceName"],
                "correlation_id": a["correlationId"],
                "timestamp": a["timestamp"],
                "blok": log["blockNumber"],
                "tx_hash": log["transactionHash"].hex(),
            })

        koraci.sort(key=lambda k: k["timestamp"], reverse=True)

        return {
            "povezan": True,
            "mreza": {
                "rpc": os.getenv("BLOCKCHAIN_RPC_URL"),
                "chain_id": w3.eth.chain_id,
                "broj_blokova": w3.eth.block_number,
            },
            "ugovor": {
                "adresa": self.contract.address,
                "vlasnik": vlasnik,
                "ukupno_koraka": ukupno_koraka,
            },
            "statistika": {
                "po_statusu": po_statusu,
                "po_servisu": po_servisu,
                "narudzbina_sa_zapisom": len(narudzbine),
                "kompenzovanih_saga": len(kompenzovane),
            },
            "poslednji_koraci": koraci[:15],
        }

    async def get_statistics(self):
        """Vraca stanje blokcejn mreze i statistiku revizijskog traga."""
        if not self.enabled:
            return {"povezan": False, "razlog": "Blokcejn klijent nije konfigurisan."}
        try:
            return await asyncio.to_thread(self._procitaj_statistiku)
        except Exception as e:
            logger.error("Neuspelo citanje statistike sa blokcejna: %s", e)
            return {"povezan": False, "razlog": str(e)}


def hesiraj(podaci: dict) -> bytes:
    return Web3.keccak(text=json.dumps(podaci, sort_keys=True, ensure_ascii=False))