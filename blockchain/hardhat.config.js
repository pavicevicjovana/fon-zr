require("@nomicfoundation/hardhat-ethers");

module.exports = {
 
  solidity: "0.8.24",

  networks: {
    docker: {
      url: "http://hardhat:8545"
    },
    localhost: {
      url: "http://127.0.0.1:8545"
    }
  },

  paths: {
    sources: "./contracts",
    scripts: "./scripts",
    artifacts: "./artifacts",
    cache: "./cache"
  }
};