# detect_once.py
import argparse, json, cv2
from pathlib import Path
from sift_core import run_sift_on_rois, load_roi_config

OUT_IMG = Path("out/annotated.png")
OUT_JSON = Path("out/matches.json")
Path("out").mkdir(exist_ok=True, parents=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", required=True, help="Path to screenshot")
    ap.add_argument("--templates", required=True, help="Dir with hero templates")
    args = ap.parse_args()

    rois = load_roi_config("config/roi_config.json")
    annotated, results = run_sift_on_rois(args.screen, args.templates, rois)

    cv2.imwrite(str(OUT_IMG), annotated)
    with open(OUT_JSON, "w") as f:
        json.dump({"results": results}, f, indent=2)
    print(f"Annotated -> {OUT_IMG}")
    print(f"JSON      -> {OUT_JSON}")

if __name__ == "__main__":
    main()
