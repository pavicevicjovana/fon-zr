// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SagaAudit {

    address public owner;

    mapping(address => bool) public authorizedServices;

    enum StepStatus { SUCCESS, FAILED, COMPENSATED }

    struct SagaStep {
        string stepName;        
        StepStatus status;      
        string serviceName;     
        string correlationId;   
        bytes32 payloadHash;    
        uint256 timestamp;      
        address recordedBy;     
    }

    mapping(uint256 => SagaStep[]) private stepsByOrder;

    uint256 public totalSteps;

    event StepLogged(
        uint256 indexed orderId,
        string stepName,
        StepStatus status,
        string serviceName,
        string correlationId,
        uint256 timestamp
    );

    event ServiceAuthorized(address indexed service);
    event ServiceRevoked(address indexed service);

    constructor() {
        owner = msg.sender;
        authorizedServices[msg.sender] = true;
        emit ServiceAuthorized(msg.sender);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Niste vlasnik ugovora!");
        _; 
    }

    modifier onlyAuthorized() {
        require(authorizedServices[msg.sender], "Servis nije autorizovan!");
        _;
    }

    function authorizeService(address service) external onlyOwner {
        require(service != address(0), "NULA_ADRESA");
        authorizedServices[service] = true;
        emit ServiceAuthorized(service);
    }

    function revokeService(address service) external onlyOwner {
        authorizedServices[service] = false;
        emit ServiceRevoked(service);
    }

    function logStep(
        uint256 orderId,
        string calldata stepName,
        StepStatus status,
        string calldata serviceName,
        string calldata correlationId,
        bytes32 payloadHash
    ) external onlyAuthorized {
        require(bytes(stepName).length > 0, "Naziv koraka je prazan!");
        require(bytes(stepName).length <= 64, "Naziv koraka je predugacak!");

        stepsByOrder[orderId].push(SagaStep({
            stepName: stepName,
            status: status,
            serviceName: serviceName,
            correlationId: correlationId,
            payloadHash: payloadHash,
            timestamp: block.timestamp,
            recordedBy: msg.sender
        }));

        totalSteps++;

        emit StepLogged(orderId, stepName, status, serviceName, correlationId, block.timestamp);
    }

    function getSteps(uint256 orderId) external view returns (SagaStep[] memory) {
        return stepsByOrder[orderId];
    }

    function getStepCount(uint256 orderId) external view returns (uint256) {
        return stepsByOrder[orderId].length;
    }

    function getStep(uint256 orderId, uint256 index) external view returns (SagaStep memory) {
        require(index < stepsByOrder[orderId].length, "Korak ne postoji!");
        return stepsByOrder[orderId][index];
    }
}
