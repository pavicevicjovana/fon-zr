const hre = require("hardhat");

const OCEKIVANA_ADRESA = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

async function main() {
  
  const [vlasnik, ordersNalog, catalogNalog, ordersConsumerNalog] =
    await hre.ethers.getSigners();

  console.log("=".repeat(70));
  console.log("SagaAudit - postavljanje na lokalnu privatnu mrezu");
  console.log("=".repeat(70));

  const SagaAudit = await hre.ethers.getContractFactory("SagaAudit");
  let ugovor;

  const bajtkod = await hre.ethers.provider.getCode(OCEKIVANA_ADRESA);

  if (bajtkod !== "0x") {
    console.log("Ugovor vec postoji na adresi:", OCEKIVANA_ADRESA);
    console.log("Deploy se preskace.");
    ugovor = SagaAudit.attach(OCEKIVANA_ADRESA);
  } else {
    console.log("Vlasnik (deployer):", vlasnik.address);
    ugovor = await SagaAudit.deploy();
    await ugovor.waitForDeployment();
    const adresa = await ugovor.getAddress();
    console.log("Ugovor postavljen na adresu:", adresa);

    if (adresa.toLowerCase() !== OCEKIVANA_ADRESA.toLowerCase()) {
      console.error("\nGRESKA: adresa ugovora nije ocekivana!");
      console.error("  ocekivano:", OCEKIVANA_ADRESA);
      console.error("  dobijeno :", adresa);
      console.error("Nalog #0 je vec slao transakcije pre deploy-a.");
      console.error("Resenje: docker compose rm -sf hardhat, pa ponovo up.");
      process.exit(1);
    }
  }

  console.log("\nServisni nalozi:");

  const nalozi = [
    { opis: "orders-service (HTTP)    ", nalog: ordersNalog },
    { opis: "product-catalog-service  ", nalog: catalogNalog },
    { opis: "orders-service (consumer)", nalog: ordersConsumerNalog },
  ];

  for (const { opis, nalog } of nalozi) {
    const vecAutorizovan = await ugovor.authorizedServices(nalog.address);

    if (vecAutorizovan) {
      console.log("  " + opis + " -> " + nalog.address + "  (vec autorizovan)");
    } else {
      await (await ugovor.authorizeService(nalog.address)).wait();
      console.log("  " + opis + " -> " + nalog.address + "  (autorizovan)");
    }
  }

  console.log("\nProvera dozvola:");
  let sveOk = true;
  for (const { opis, nalog } of nalozi) {
    const ok = await ugovor.authorizedServices(nalog.address);
    console.log("  " + opis + " :", ok);
    if (!ok) sveOk = false;
  }

  if (!sveOk) {
    console.error("\nGRESKA: nisu svi nalozi autorizovani.");
    process.exit(1);
  }

  console.log("\nGotovo. Ugovor je spreman za upis Saga koraka.");
  console.log("=".repeat(70));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});