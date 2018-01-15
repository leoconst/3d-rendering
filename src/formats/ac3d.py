SIGNATURE = 'AC3D'

VERSION = 11
VERSION_CHAR = format(VERSION, 'x')

TOKENS = {
    name
        data
    texture
    texrep
    rot
    loc
    url
    numvert
    numsurf
        SURF
        mat
        refs
    kids
}


def load(file):
    """ Read a .cbt formatted file and return its points and triangles.
    """
    with open(file, 'r') as stream:

        # Read the signature:
        signature = stream.read(4)
        if signature != SIGNATURE:
            raise SyntaxError(
                f'Invalid signature: {signature!r} != {SIGNATURE}.')

        # Read the version char:
        version_char = stream.read(1)
        version = int(version_char, base=16)

        for line in stream:
            line = line.strip()

            # Read points.
            if line.startswith('numvert'):
                point_count = int(line[8:])

                for _ in range(point_count):
                    line = next(stream)


    return points, triangles


def save(file, points=(), triangles=()):
    pass
