# LiveSatProto
Prototype for tracking real-time satellite positions in orbit.

<img src="https://github.com/user-attachments/assets/2f18b768-c425-4699-9fd0-fcd06a7a1246" width=410 />

### Use
```bash
$ livesat-proto <launch_time> <angle> <latitude> <longitude>
{
  "satellite_position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 500
  },
  "timestamp": "2025-01-24T15:45:00Z"
}

## Requirements:
# To track the current position of a satellite, the following parameters are required: 
# Launch Time: The time the satellite was launched (ISO 8601 format).
# Angle: The angle of the satellite’s trajectory.
# Latitude: The current latitude of the satellite.
# Longitude: The current longitude of the satellite.
#Altitude: The altitude (in meters) of the satellite from the Earth’s surface.
```
### Dev
```bash
$ git clone ...
$ pdm venv create
$ source .venv/bin/activate
$ pdm install
$ pytest
```

