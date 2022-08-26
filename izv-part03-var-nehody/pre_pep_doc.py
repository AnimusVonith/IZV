# coding=utf-8
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
# muzete pridat vlastni knihovny

def get_data(df: pd.DataFrame) -> str:
    alcohol_scope = [1,3,6,7,8,9]
    df = df.copy()
    df = df[df["p11"].isin(alcohol_scope)]
    df["p11"].replace([1, 3, 6, 7, 8, 9],
                      ["0.01-0.24",
                       "0.24-0.50", "0.50-0.80",
                       "0.80-1.00", "1.00-1.50",
                       "1.50+"], inplace=True)

    plt.figure(figsize=(8,6))
    sns.countplot(data=df, x="p11", order=["0.01-0.24",
                       "0.24-0.50", "0.50-0.80",
                       "0.80-1.00", "1.00-1.50",
                       "1.50+"])
    plt.ylabel("Počet vinníkov")
    plt.xlabel("Podieľ alkoholu v krvi (promile)")
    plt.title("Rozdelenie podľa promile alkoholu u vinníkov autonehôd", size=15, weight="bold")
    
    plt.savefig("fig.jpg")
    #plt.show()

    results = []
    results.append(["promile", "počet"])
    for x in sorted(df["p11"].unique()):
        row = []
        row.append(x)
        row.append(str(df[df["p11"]==x]["p11"].count()))
        results.append(row)
    return results


if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    """
    for x in sorted(df["p11"].unique()):
        print(f'''{x} {df[df["p11"]==x]["p11"].count()}''')
    """
    results = get_data(df)
    for row in results:
        print("%9s\t%5s" % (row[0], row[1]))
        
