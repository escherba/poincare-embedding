from __future__ import print_function, division, absolute_import, unicode_literals
import numpy as np
import argparse
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')


def transitive_isometry(t1, t0):
    u'''
    computing isometry which move t1 to t0
    '''

    (x1, y1), (x0, y0) = t1, t0

    def to_h(z):
        return (1 + z) / (1 - z) * complex(0, 1)

    def from_h(h):
        return (h - complex(0, 1)) / (h + complex(0, 1))

    z1 = complex(x1, y1)
    z0 = complex(x0, y0)

    h1 = to_h(z1)
    h0 = to_h(z0)

    def f(h):
        assert(h0.imag > 0)
        assert(h1.imag > 0)
        return h0.imag / h1.imag * (h - h1.real) + h0.real

    def ret(z):
        z = complex(z[0], z[1])
        h = to_h(z)
        h = f(h)
        z = from_h(h)
        return z.real, z.imag

    return ret


def unique(tokens):
    result = []
    seen = set()
    for token in tokens:
        if token not in seen:
            result.append(token)
            seen.add(token)
    return result


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('embedding_file', type=str)
    parser.add_argument('--labels', type=str, default=None)
    parser.add_argument('--targets', type=str, nargs='*', default=None)
    parser.add_argument('--center', type=str, default=None)
    return parser.parse_args()


def main():

    args = parse_args()

    # load embeddings
    embedding_file = args.embedding_file
    print("read embedding_file:", embedding_file)
    embeddings = pd.read_csv(embedding_file, header=None, sep="\t", dtype={0: 'str', 1: np.float64, 2: np.float64})
    embeddings.set_index(0, inplace=True)

    if args.labels is not None:
        labels = pd.read_csv(args.labels, header=None, sep="\t", dtype={0: 'str', 1: 'str'})
        labels.set_index(0, inplace=True)
        labels = labels.to_dict()[1]
    else:
        labels = {}

    if args.targets is None:
        targets = embeddings.index
    else:
        targets = args.targets

    targets = unique(targets)
    print(len(targets), ' targets found')

    _ = plt.figure(figsize=(10, 10))
    ax = plt.gca()
    ax.cla()  # clear things for fresh plot

    ax.set_xlim((-1.1, 1.1))
    ax.set_ylim((-1.1, 1.1))

    circle = plt.Circle((0, 0), 1., color='black', fill=False)
    ax.add_artist(circle)

    if args.center is not None:
        z = embeddings.loc[args.center]
        isom = transitive_isometry((z.at[1], z.at[2]), (0, 0))

    for n in targets:
        z = embeddings.loc[n]
        if isinstance(z, pd.DataFrame):
            continue  # if the index is non-unique
        print(z.at[1], z.at[2])
        if args.center is not None:
            x, y = isom((z.at[1], z.at[2]))
        else:
            x, y = z.at[1], z.at[2]
        print(z, x, y)
        if args.center is not None and n == args.center:
            ax.plot(x, y, 'o', color='g')
            ax.text(x + 0.001, y + 0.001, labels.get(n, n), color='r', alpha=0.6)
        else:
            ax.plot(x, y, 'o', color='y')
            ax.text(x + 0.001, y + 0.001, labels.get(n, n), color='b', alpha=0.6)
    plt.show()


if __name__ == '__main__':
    main()
