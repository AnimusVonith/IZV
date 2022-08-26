# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzete pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovanim"""
    df = df.dropna(subset=["d", "e"])
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody
    (dalnice vs prvni trida) pro roky 2018-2020 """

    regions = ['PHA','STC','JHC','PLK','ULK','HKK','JHM','MSK','OLK','ZLK','VYS','PAK','LBK','KVK']
    roky = [2018, 2019, 2020]
    typy = ["dialnica", "cesta 1. triedy"]
    region = "JHM"
    gdf = gdf.copy()
    if region in regions:
        gdf = gdf[gdf["region"] == region]

    gdf = gdf[["p2a", "p36", "geometry"]]
    gdf = gdf[~gdf.is_empty]

    gdf["p2a"] = gdf["p2a"].astype("datetime64")
    gdf["rok"] = gdf["p2a"].dt.year
    
    gdf["dialnica"] = gdf["p36"] == 0
    gdf["cesta 1. triedy"] = gdf["p36"] == 1

    fig, axs = plt.subplots(2, 3, figsize=(18,8))
    gdf = gdf[gdf["rok"].isin(roky)]
    
    colors=[["#FF91AF", "#D3212D", "#A52A2A"], ["#7FFFD4", "#007FFF", "#89CFF0"]]
    for i, rok in enumerate(roky):
        holder = gdf[gdf["rok"] == rok]
        for j, typ in enumerate(typy):
            holder[holder[typ]].plot(ax=axs[j, i], color=colors[j][i], marker=".", markersize=5)
            axs[j, i].title.set_text(f"{rok} {typ}")
            axs[j, i].set_aspect("auto")
            axs[j, i].axis("off")
            ctx.add_basemap(axs[j, i], crs=holder.crs, source=ctx.providers.Stamen.TonerLite)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.029, right=0.955)
    
    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """

    regions = ['PHA','STC','JHC','PLK','ULK','HKK','JHM','MSK','OLK','ZLK','VYS','PAK','LBK','KVK']
    gdf_c = gdf.copy()[gdf["region"] == "JHM"]
    gdf_c = gdf_c[gdf_c["p36"] == 1]
    gdf_c["area"] = gdf_c.area
    gdf_c = gdf_c.set_geometry(gdf_c.centroid)
    gdf_c = gdf_c.to_crs(epsg=3857)

    coords = np.dstack([gdf_c.geometry.x, gdf_c.geometry.y]).reshape(-1,2)
    model = sklearn.cluster.MiniBatchKMeans(n_clusters = 75)
    db = model.fit(coords)
    gdf4 = gdf_c.copy()
    gdf4["cluster"] = db.labels_
    gdf4 = gdf4.dissolve(by="cluster", aggfunc={"p1": "count", "area":"sum"}).rename(columns={"p1":"cnt"})

    plt.figure(figsize=(15, 8))
    ax = plt.gca()
    ax.axis("off")
    gdf4.plot(ax=ax, column="cnt", legend=True, marker=".") 
    ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.Stamen.TonerLite)

    if fig_location is not None:
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
