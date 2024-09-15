# ISS Recovery repository
This repository holds all of the scripts necessary for calculations related to the Spaceshot Recovery team.

As of september 2024, this project has been assimilated into the Spaceshot Avionics Team Support Project, which aims to increase ease-of-use for commonly used tools across different projects within Spaceshot.

### API 
Combines parachute simulation and energetic calculator into easy-to-use endpoints:

**API Schema**
`/`

> `/chute` : Endpoint for all parachute-related calculators

>> POST `/size` : Given some parachute and rocket parameters, determines chute size (unimplemented)

>> POST `/sim` : Given parachute and rocket parameters, determines descent profile for the vehicle. (unimplemented, asynchronous)

>> POST `/montecarlo` : Performs advanced analysis of chute simulation, granting access to more advanced statistics (such as opening shock calculations) (unimplemented, asynchronous)

> `/energetic` : Endpoint for energetic-related calculators

>> POST `/sim` : Returns the required energetic masses for all `ESimData` schemas passed into this endpoint. Used for charge sizing. Returns as an array of `ESimResult` schemas.

>> POST `/rcm` : Returns the calculated efficiency for an ejection charge given mass and pressure parameters (Used for RCM/vacuum testing). Takes in the `RCMParam` schema and returns a single number between 0-1, signifying the energetic mass efficiency.

>> POST `/mass`: Returns the calculated efficiency for an ejection charge given only mass parameters (This is almost guaranteed to be inaccurate). It is useful as a sanity check. Takes in a `MassParam` schema and returns a single number from 0-1, like `/rcm`



#### Data schemas - Parameters
`ESimData`
```json
{
    "name": "Stargazer 1 Sustainer", // String name for the simulation
    "dimensions": {
        "diameter": 0.0762,          // Diameter of section (in INCHES)
        "length": 0.127              // Length of section (in INCHES)
    },
    "target_pressure": 16,           // Pressure to seperate (psi)
    "efficiency": [0.9]              // Array of mass combustion efficiency values for the energetic (Dimensionless, between 0-1).
                                     // Each entry in the array will correspond to its own calculated energetic value.
}
```

`RCMParam`
```json
{
    "volume": 0.5,                   // Volume of test chamber (in in^3)
    "datapoints": [
        [
            1,                       // Mass (in grams) of the energetic
            1.04608,                 // Peak pressure (in BAR)
            0.166255,                // Reference pressure (in BAR)
        ]
        // ...
    ]
}
```

`MassParam`
```json
[
    1,                               // Mass (in grams) of the energetic
    1.5,                             // "Wet" mass of energetic test structure (Structure + energetic)
    0.5                              // "Dry" mass of energetic test structure (Just Structure)
]
```

#### Data schemas - Returns
Single value returns will always be of form
```json
{
    "result": 1.23 // value
}
```


`ESimResult`
```json
{
    "name": "Stargazer 1 Sustainer", // String name for the simulation
    "sims": [
        {
            "efficiency": 0.9,
            "result": 1.02           // Sizing result (in GRAMS)
        }
        // ...
    ]
}

```


#### Parachute-Simulation
Simulation and calculation of parachutes / parachute sizing.