| tag value  | n | array  | description |
| --- | --- | --- | --- |
| pos              | #particles | float ** | return array of particles position (size=n*3) |
| vel              | #particles | float ** | return array of particles velocitie  (size=n*3)|
| mass              | #particles | float ** | return array of particles velocitie  (size=n)|
| acc              | #particles | float ** | return array of particles acceleration  (size=n*3)|
| pot              | #particles | float ** | return array of particles potential  (size=n)|
| rho              | #particles | float ** | return array of particles density  (size=n)|
| hsml              | #particles | float ** | return array of particles hydro smooth length   (size=n)|
| temp              | #particles | float ** | return array of particles temperature   (size=n)|
| age              | #particles | float ** | return array of particles age   (size=n)|
| metal              | #particles | float ** | return array of particles metallicity   (size=n)|
| u              | #particles | float ** | return array of particles internal energy  (size=n)|
| id              | #particles | int ** | return array of particles index  (size=n)|
| aux              | #particles | float ** | return auxiliary array  (size=n)|
| keys              | #particles | float ** | return keys array  (size=n)|

| tag value  | value  | description |
| --- | --- | --- |
| ngas           | int *        | #gas particles |
| nhalo           | int *        | #dark matter particles |
| ndisk           | int *        | #old stars particles |
| nstars          | int *        | #stars particles |
| nbulge           | int *        | #bulge particles |
| nbndry           | int *        | #bndry particles |
| nsel           | int *        | #selected particles |
| time           | float *        | snapshot time |