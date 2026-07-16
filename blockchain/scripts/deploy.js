const hre = require("hardhat");

const OCEKIVANA_ADRESA = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

async function main() {
  
  const [vlasnik, ordersNalog, catalogNalog] = await hre.ethers.getSigners();

  console.log("=".repeat(70));
  console.log("Postavljanje SagaAudit ugovora na lokalnu privatnu mrezu");
  console.log("=".repeat(70));
  console.log("Vlasnik (deployer):", vlasnik.address);

  const SagaAudit = await hre.ethers.getContractFactory("SagaAudit");
  const ugovor = await SagaAudit.deploy();

  await ugovor.waitForDeployment();
  const adresa = await ugovor.getAddress();

  console.log("Ugovor postavljen na adresu:", adresa);

  if (adresa.toLowerCase() !== OCEKIVANA_ADRESA.toLowerCase()) {
    console.error("\nGRESKA: adresa ugovora nije ocekivana!");
    console.error("  ocekivano:", OCEKIVANA_ADRESA);
    console.error("  dobijeno :", adresa);
    console.error("Mreza verovatno nije sveza. Resenje: docker compose down -v pa ponovo up.");
    process.exit(1);
  }

  console.log("\nAutorizacija servisnih naloga:");

  await (await ugovor.authorizeService(ordersNalog.address)).wait();
  console.log("  orders-service         ->", ordersNalog.address);

  await (await ugovor.authorizeService(catalogNalog.address)).wait();
  console.log("  product-catalog-service ->", catalogNalog.address);

  const ordersOk = await ugovor.authorizedServices(ordersNalog.address);
  const catalogOk = await ugovor.authorizedServices(catalogNalog.address);

  console.log("\nProvera dozvola:");
  console.log("  orders autorizovan :", ordersOk);
  console.log("  catalog autorizovan:", catalogOk);

  console.log("\nGotovo. Ugovor je spreman za upis Saga koraka.");
  console.log("=".repeat(70));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});