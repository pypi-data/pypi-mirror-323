import argparse

from gridding import GPS, Grid, hash, Resolution, string2bytearray


def main(args):
    """
    Get a tile ID from GPS coordinates

    Arguments
    ---------
    -x --longitude: float
        the longitude in decimal degrees
    -y --latitude: float
        the latitude in decimal degrees
    -r --resolution: str
        the grid resolution, eg. `200m`
    -o --obfuscate
        add flag to get a hashed result
    -t --tile
        add flag to return the tile coordinates instead of the carreau id

    Usage
    -----
    $ python -m gridding -x -2.342808 -y 48.877198 -r 200m
    """
    resolution = Resolution.FromString(args.resolution)
    grid = Grid(resolution)
    longitude = float(args.longitude.replace(",", "."))
    latitude = float(args.latitude.replace(",", "."))
    carreau, tile = grid.from_gps(GPS(longitude, latitude))
    if args.tile:
        print(tile.to_string())
    else:
        if args.obfuscate:
            print(hash(string2bytearray(carreau)).hex())
        else:
            print(carreau)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-x", "--longitude", help="the longitude in decimal degrees", required=True
    )
    parser.add_argument(
        "-y", "--latitude", help="the latitude in decimal degrees", required=True
    )
    parser.add_argument(
        "-r", "--resolution", help="the grid resolution, eg. '200m'", required=True
    )
    parser.add_argument(
        "-o",
        "--obfuscate",
        help="add to return a hashed result (default: no)",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-t",
        "--tile",
        help="add to return the tile coordinates (default: no)",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    main(args)
