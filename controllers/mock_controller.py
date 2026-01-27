"""Mock temperature controller for testing without hardware."""
import random
import time


class MockTemperatureController:
    """
    Mock controller that simulates temperature readings.

    Use this for testing the GUI without real hardware connected.
    """

    def __init__(self, port='COM5', device_ids=None, json_file=None):
        """
        Initialize mock temperature controller.

        Args:
            port: Serial port (ignored, for API compatibility)
            device_ids: List of Modbus device IDs (default [1, 2, 3])
            json_file: Path to register configuration JSON (ignored)
        """
        if device_ids is None:
            device_ids = [1, 2, 3]

        self.port = port
        self.device_ids = device_ids

        # Initialize simulated temperatures for each device/zone
        # Structure: {device_id: [zone1_temp, zone2_temp, ...]}
        self._temperatures = {}
        for device_id in device_ids:
            # Start with realistic temperatures (20-30°C range)
            self._temperatures[device_id] = [
                random.uniform(22.0, 28.0) for _ in range(6)
            ]

        # Target temperatures for drift simulation
        self._targets = {}
        for device_id in device_ids:
            self._targets[device_id] = [
                random.uniform(20.0, 35.0) for _ in range(6)
            ]

    def read_temperature(self, device_id, zone):
        """
        Read temperature for a specific zone on a device.

        Args:
            device_id: Modbus device address
            zone: Zone number (1-6)

        Returns:
            Temperature in degrees Celsius as float
        """
        # Small delay to simulate communication
        time.sleep(0.05)

        if device_id not in self._temperatures:
            raise KeyError(f"Device {device_id} not initialized")

        zone_idx = zone - 1
        if zone_idx < 0 or zone_idx >= 6:
            raise ValueError(f"Invalid zone number: {zone}")

        # Simulate temperature drift toward target with noise
        current = self._temperatures[device_id][zone_idx]
        target = self._targets[device_id][zone_idx]

        # Drift toward target (0.1°C per reading on average)
        drift = (target - current) * 0.05
        noise = random.uniform(-0.3, 0.3)

        new_temp = current + drift + noise
        self._temperatures[device_id][zone_idx] = new_temp

        # Occasionally change target to keep things interesting
        if random.random() < 0.01:  # 1% chance per reading
            self._targets[device_id][zone_idx] = random.uniform(20.0, 35.0)

        return new_temp

    def close(self):
        """Close connections (no-op for mock)."""
        pass
