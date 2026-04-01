// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EventLogger {
    struct Event {
        string eventType;
        uint256 timestamp;
        string cameraId;
        string location;
        string clipHash;
        string ipfsCid;
        uint256 confidence;
        address reportedBy;
    }

    mapping(uint256 => Event) public events;
    uint256 public eventCount;
    address public owner;

    event EventLogged(
        uint256 indexed id,
        string eventType,
        uint256 timestamp,
        string clipHash
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logEvent(
        string memory eventType,
        string memory cameraId,
        string memory location,
        string memory clipHash,
        string memory ipfsCid,
        uint256 confidence
    ) public onlyOwner {
        eventCount += 1;
        events[eventCount] = Event({
            eventType: eventType,
            timestamp: block.timestamp,
            cameraId: cameraId,
            location: location,
            clipHash: clipHash,
            ipfsCid: ipfsCid,
            confidence: confidence,
            reportedBy: msg.sender
        });

        emit EventLogged(eventCount, eventType, block.timestamp, clipHash);
    }

    function getEvent(uint256 id) public view returns (Event memory) {
        require(id > 0 && id <= eventCount, "Event does not exist");
        return events[id];
    }
}
