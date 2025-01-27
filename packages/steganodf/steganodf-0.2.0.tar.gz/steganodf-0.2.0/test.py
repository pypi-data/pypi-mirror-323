import polars as pl
from tqdm import tqdm
import numpy as np
import string
import random

from steganodf.algorithms import BitPool


def create_error(mdf, percent):

    df_encoded = mdf.to_pandas()
    size = df_encoded.shape[0] * df_encoded.shape[1]
    cells = list(range(0, size))
    count = int(percent * size / 100)
    cells = random.sample(cells, count)
    for index in cells:
        x = index % df_encoded.shape[0]
        y = index // df_encoded.shape[0]
        df_encoded.iat[x, y] = random.randint(0, 1000)

    return pl.from_pandas(df_encoded)


N = 1_000_000
# Créer un DataFrame Polars à partir des données
df = pl.DataFrame({"a": np.random.rand(N), "b": np.random.rand(N)})


sdf = df.head(10000)
payload = string.ascii_lowercase[:5].encode()

results = []

for p in tqdm(range(1, 50, 1)):
    a = BitPool(block_size=5, parity_size=p)
    edf = a.encode(sdf, payload)
    mmax = -1

    for e in range(0, 100):
        ndf = create_error(edf, e)
        rp = a.decode(ndf)
        if rp != payload:
            mmax = e
            break

    results.append({"mmax": mmax, "parity": p})


print("done")
rdf = pl.DataFrame(results)

rdf.write_parquet("test.parquet")
