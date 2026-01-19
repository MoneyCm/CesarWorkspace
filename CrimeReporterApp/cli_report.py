
import argparse, glob
import pandas as pd
from report_engine import load_multiple_files, build_report

def main():
    ap = argparse.ArgumentParser(description="Genera reporte Excel desde archivos SIEDCO/DIJIN (.xlsx)")
    ap.add_argument("--in", dest="inputs", nargs="+", required=True, help="Rutas de entrada (archivos o patrones)")
    ap.add_argument("--out", dest="out", required=True, help="Ruta de salida .xlsx")
    ap.add_argument("--municipio", dest="municipio", default=None, help="Municipio foco (opcional)")
    args = ap.parse_args()

    paths = []
    for p in args.inputs:
        paths.extend(glob.glob(p))

    if not paths:
        raise SystemExit("No se encontraron archivos de entrada.")

    # cargar como binarios para reutilizar motor
    files = [open(p, "rb") for p in paths]

    dfs, logs = load_multiple_files(files, normalize_city=True)
    for f in files:
        try: f.close()
        except: pass

    full = pd.concat(dfs, ignore_index=True)
    if args.municipio:
        full = full[full["MUNICIPIO"].str.contains(args.municipio, case=False, na=False)]

    xls_bytes = build_report(full)
    with open(args.out, "wb") as fh:
        fh.write(xls_bytes)

    print("Listo:", args.out)
    for l in logs:
        print(l)

if __name__ == "__main__":
    main()
