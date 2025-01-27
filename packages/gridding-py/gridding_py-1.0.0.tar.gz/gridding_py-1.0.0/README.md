# gridding
_Build geographical grids in Python_

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/cyrildever/gridding)
![GitHub last commit](https://img.shields.io/github/last-commit/cyrildever/gridding)
![GitHub issues](https://img.shields.io/github/issues/cyrildever/gridding)
![GitHub license](https://img.shields.io/github/license/cyrildever/gridding)
![PyPI - Version](https://img.shields.io/pypi/v/gridding-py)

This is a Python library implementing the "carroyage" for geographical data.

### Motivation

In order to be able to make analysis in the more granular level of the "carreau", this provides an easy reference to building custom grids by allowing to assign a unique tile / "carreau" ID to a geographical coordinate (latitude, longitude) or a French postal address.

Indeed, the result of the computation gives the ID according to the [EU directive INSPIRE](https://www.insee.fr/fr/information/5008701?sommaire=5008710#titre-bloc-14) in the following format:
`WGS84|RES200m|N2471400|E0486123`
that could be decomposed as a pipe-separated string with:
- the projection system, eg. `WGS84`;
- the resolution of the grid, ie. the size of the square, eg. `RES200m` for $200\text{ m}$;
- the bottom-left point of the grid's bounding box defined by:
  * its latitude in decimal degrees, eg. `N2471400` for $\text{N }24.714000°$;
  * its longitude, eg. `E0486123` for $\text{E }4.861230°$;

as well as the coordinate in the grid in the form of `<row>.<column>` from the initial bottom-left point.

It would need as input parameters:
- the coordinates of the initial point of the grid (by default the bottom-left point of the bounding box covering the French metropolitan territory: $\text{N }41.316666°$ / $\text{W }5.151110$);
- the size and scale of the grid, eg. `200m`, `1km`, ...;
- the projection system (default: `WGS84`).

Below are the calculation bases.

### Geographic Information System (GIS) computations

#### <u>Latitude</u>

In `WGS84`, one degree of latitude is almost equivalent to $111\text{ km}$ everywhere on Earth.

The distance in meter, $D_{lat}$, for one degree in latitude is given by the following formula:
```math
D_{lat} = \pi \cdot \frac{a (1 - e^2)}{(1 - e^2 \sin^2(\text{latitude}))^{3/2}} \times \frac{1}{180}
```
where
- $a$ is the semi-major axis of the Earth's ellipsoid (in `WGS84`, $a = 6378137$);
- $e$ is the excentricity of the ellipsoid, given by:
```math
e = \sqrt{1 - \frac{b^2}{a^2}}
```
  (in `WGS84`, $b = 6356752.3142$)
- $latitude$ is the latitude of the point in radians.

From here, one can compute the degree in latitude for any size of tile / "carreau", eg. in `WGS84`, a "carreau" of height $200\text{ m} \approx 0.001796°$:

```math
\Delta latitude = \frac{distance}{D_{lat}}
```
where
- $distance$ is the vertical distance to convert in degrees of latitude, eg. $200$;
- $D_{lat}$ is the result of the computation above around the given $latitude$.

#### <u>Longitude</u>

The variation of longitude as a function of latitude is calculated by taking into account the decrease in the distance between the meridians as one moves away from the equator. This decrease is due to the fact that the Earth is spherical.

In `WGS84`, the formula that allows one to calculate the distance corresponding to a degree of longitude as a function of a latitude is the following:
```math
\Delta{longitude} = \frac{distance}{D_{lon} \times \cos(latitude)}
```
where
- $distance$ is the horizontal distance to convert in degrees of longitude, eg. $200$;
- $latitude$ is the starting point expressed in radians, eg. $45° = \frac{\pi}{4}$;
- $D_{lon}$ is the result of the computation below at the given $latitude$:

```math
D_\text{lon} = \pi \cdot a \cdot \cos(\text{latitude}) \cdot \frac{1}{180} \cdot \frac{1}{\sqrt{1 - e^2 \sin^2(\text{latitude})}}
```

#### <u>XY coordinates</u>

The UTM projection would be used to handle XY coordinates with the central longitude $\lambda_0$ being automatically calculated for the UTM zone with the longitude of the searched point, _eg._ $-3°$ _for the UTM zone `30T` covering France from_ $W 6°$ _to_ $0°$.

The following data and formula would be used in that case: _eg. for `WGS84`_
- $a = 6378137$
- $e = 0.0818191908426$
- $k_0 = 0.9996$
- $\varphi = latitude \times \frac{\pi}{180}$
- $\lambda = longitude \times \frac{\pi}{180}$
- $N = \frac{a}{\sqrt{1 - e^2\sin^2(\phi)}}$
- $T = \tan^2(\varphi)$
- $C = \frac{e^2\cos^2(\varphi)}{1 - e^2}$
- $A = (\lambda - \lambda_0)\cos(\varphi)$
- $M = a \left( (1 - \frac{e^2}{4} - \frac{3 e^4}{64} - \frac{5 e^6}{256}) \varphi - (\frac{3 e^2}{8} + \frac{3 e^4}{32} + \frac{45 e^6}{1024}) \sin(2 \varphi) + (\frac{15 e^4}{256} + \frac{45 e^6}{1024}) \sin(4 \varphi) - (\frac{35 e^6}{3072}) \sin(6 \varphi) \right)$

One can now compute the XY coordinates as follows:
- $X = k_0 \left( N ( A + \frac{(1 - T + C) A^3}{6} + \frac{(5 - 18 T + T^2 + 72 C - 58 e^2) A^5}{120} ) \right) + 500000$
- $Y = k_0 \left( M + N \tan(\varphi) ( \frac{A^2}{2} + \frac{(5 - T + 9 C + 4 C^2) A^4}{24} + \frac{(61 - 58 T + T^2 + 600 C - 330 e^2) A^6}{720} ) \right)$

_NB: If the searched point is in the south, add_ $10,000,000$ _to_ $Y$ _to avoid negative coordinates._

With all these formulas, one is now able to build a full system placing any GPS or XY coordinates into a unique "carreau". This library implements one way to do it.


### Install

```console
$ git clone https://github.com/cyrildever/gridding.git
$ cd gridding/packages/py/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install build twine
```


### Usage

```console
pip install gridding-py
```

If you want to use the `from_address()` feature, you need to build or upload the [address repository](https://huggingface.co/datasets/cyrildever/gridding/blob/main/fr_address_repository.csv.gz).

Your one-line address must be compliant with the following guidelines:
- elements must be in the following order: `<numero> <repetitor> <voie> <lieu_dit> <cp> <ville>`;
- `<numero>` is the street number;
- `<repetitor>` is the eventual addition to the number, eg. `bis`, `ter`, ...;
- `<voie>` is the street name including its type;
- `<lieu_dit>` is a distinct locality (neither the city nor a postal box information);
- `<cp>` is the postal code in a full integer format (`2A000` must be transformed in `20000` for Corsica for example);
- `<ville>` is the city name (ideally without further information, ie. no `Arrondissement` or `Cedex` mentions).

For now, only French addresses are fully covered, but the library can work with any other country providing you build the corresponding repository.\
Feel free to add any normalizing tools through pull requests in the library to help enriching it.

#### 1) <u>Module</u>

To get the tile / "carreau" from GPS coordinates using a GPS pivot, ie. the bottom-left point of your grid:
```python
from gridding import METER, WGS84, GPS, Grid, Resolution

grid = Grid(
    Resolution(200, METER),
    GPS(-5.151110, 41.316666),
    WGS84(),
)
carreau, tile = grid.from_gps(my_point)
print(f"This GPS point belongs to the carreau with code: {carreau}, and coordinate: {tile.to_string()}")
```

**IMPORTANT**: when using negative coordinates for a pivot point, be sure to give it a `0` as 6th decimal.

To get it from a French postal address:
```python
from gridding import FR

carreau, tile = grid.from_address("9 boulevard Gouvion Saint-Cyr 75017 Paris", FR())
print(f"This address belongs to the carreau with code: {carreau}, and coordinate: {tile.to_string()}")
```

To get it from X/Y coordinates:
```python
from gridding import XY

my_point = XY(647872.07, 5110548.44, "UTM", "WGS84")
carreau, tile = grid.from_xy(my_point)
print(f"This X/Y point belongs to the carreau with code: {carreau}, and coordinate: {tile.to_string()}")
```

For now, only the `WGS-84` system is available and can be used in conjunction with the `UTM` projection if need be to get X/Y coordinates.

You may want to use the "distance" between two tiles (which returns a sort of average radius in tiles from one tile to the other):
```python
distance = Tile.Distance(tile1, tile2)
print(f"The radius between these two tiles is equal to {distance} tiles")
```
The idea here is to be able to easily know if a tile is within a certain tile distance of another, eg. two tiles away in each direction.

#### 2) <u>Script</u>

You may also use the main script to get the "carreau" from some GPS coordinates directly in a terminal, eg.
```
usage: python -m gridding [-h] -x LONGITUDE -y LATITUDE -r RESOLUTION [-o | --obfuscate | --no-obfuscate] [-t | --tile | --no-tile]

options:
  -h, --help            show this help message and exit
  -x LONGITUDE, --longitude LONGITUDE
                        the longitude in decimal degrees
  -y LATITUDE, --latitude LATITUDE
                        the latitude in decimal degrees
  -r RESOLUTION, --resolution RESOLUTION
                        the grid resolution, eg. '200m'
  -o, --obfuscate, --no-obfuscate
                        add to return a hashed result (default: no)
  -t, --tile, --no-tile
                        add to return the tile coordinates instead of the carreau id (default: no)
```
_NB: The optional obfuscated result is a unique SHA-256 hexadecimal string._


### Tests

```console
$ pip install -e . && python3 -m unittest discover
```


### License

This module is distributed under a MIT license. \
See the [LICENSE](LICENSE) file.


<hr />
&copy; 2024 Cyril Dever. All rights reserved.