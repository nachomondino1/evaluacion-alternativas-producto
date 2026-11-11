"""Exporta los Excel de data/ a JSON para el sitio estático (site/data/).

Uso (desde la raíz del repo): python scripts/export_site_data.py
Requiere pandas y openpyxl. Re-ejecutar cada vez que cambien los Excel.
La valoración por atributo se resuelve acá (igual que get_alts_final_value de la
versión Streamlit); en el navegador solo se ponderan por la importancia técnica.
"""
import json
import math
import pandas as pd

PRODUCTS = ["celulares", "smartband", "tv"]


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def table(df, with_index=True):
    return {
        "index": [clean(i) for i in df.index] if with_index else None,
        "columns": [str(c) for c in df.columns],
        "rows": [[clean(v) for v in r] for r in df.itertuples(index=False, name=None)],
    }


def export(p):
    rx = lambda path, **k: pd.read_excel(path.format(p), **k)
    df_alt = rx("data/collect_initial_data/{}/df_alt.xlsx")
    df_cl = rx("data/data_preparation/{}/df_alt_cleaned.xlsx")
    needs = rx("data/data_preparation/{}/df_cust_needs.xlsx", index_col=0)
    rel = rx("data/data_preparation/{}/df_relation_matrix.xlsx", index_col=0)
    s_alt = rx("data/modelling/atribucion/{}/df_attr_alt_sent.xlsx")
    s_val = rx("data/modelling/atribucion/{}/df_attr_values_sent.xlsx")
    cl = "data/modelling/clustering/{}/"
    c_alts = rx(cl + "df_alt_cleaned_cluster.xlsx", index_col=0)
    c_per = rx(cl + "df_alt_per_clust.xlsx", index_col=0)
    c_cent = rx(cl + "df_centroids_values.xlsx", index_col=0)
    c_brand = rx(cl + "df_brand_per_cluster.xlsx", index_col=0)
    c_best = rx(cl + "df_best_cluster_per_cust_need.xlsx", index_col=0)

    value_attrs = set(s_val["atributo"].unique())
    attrs = list(s_val["atributo"].unique()) + list(s_alt["atributo"].unique())

    shown = df_alt[df_alt.id_alternativa.isin(df_cl["id_alternativa"].unique())].reset_index(drop=True)
    shown = shown.set_index("id_alternativa", drop=False)
    sent_rows = []
    for _, row in df_cl.iterrows():
        sents = []
        for a in attrs:
            if a in value_attrs:
                v = row[a]
                sub = s_val[s_val["atributo"] == a]
                if str(v) != "nan":
                    s = sub[sub["valor"] == v]["sent"]
                    s = float(s.iloc[0]) if len(s) else None
                else:
                    s = float(sub["sent"].min())
            else:
                s = s_alt[(s_alt["atributo"] == a) & (s_alt["id_alternativa"] == row["id_alternativa"])]["sent"]
                s = float(s.iloc[0]) if len(s) else None
            sents.append(clean(s))
        sent_rows.append(sents)

    # Tabla que ve el cliente: df_alt filtrada (sin id), con el orden de df_cl
    display = shown.loc[df_cl["id_alternativa"]].iloc[:, 1:]
    out = {
        "needs": {"keys": list(needs.index), "labels": list(needs["cust_needs_three_words"])},
        "relation": table(rel),
        "attrs": attrs,
        "display": table(display, with_index=False),
        "sent": sent_rows,
        "clusters": {
            "alts": table(c_alts.iloc[:, 1:], with_index=False),
            "perCluster": table(c_per),
            "centroids": table(c_cent),
            "brands": table(c_brand),
            "best": table(c_best),
        },
    }
    missing = [a for a in rel.columns if a not in attrs]
    assert not missing, f"{p}: atributos sin sentiment: {missing}"
    with open(f"site/data/{p}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    print(p, "ok", len(df_cl), "alternativas")


if __name__ == "__main__":
    for p in PRODUCTS:
        export(p)
