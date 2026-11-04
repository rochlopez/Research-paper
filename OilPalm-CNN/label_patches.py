
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent
PREPARED_DIR = PROJECT_DIR / "prepared_data"

PATCH_FILE = PREPARED_DIR / "X_patches.npy"
SOURCE_FILE = PREPARED_DIR / "patch_sources.npy"
LABEL_FILE = PREPARED_DIR / "patch_labels.csv"

# Load prepared patches
X = np.load(PATCH_FILE).astype(np.float32)
sources = np.load(SOURCE_FILE, allow_pickle=False)

if X.ndim != 4 or X.shape[1] != 15:
    raise ValueError(f"Unexpected patch shape: {X.shape}")

# Load existing labels so your work can be resumed
if LABEL_FILE.exists():
    labels_df = pd.read_csv(LABEL_FILE)
    label_map = dict(zip(labels_df["patch_id"], labels_df["label"]))
else:
    label_map = {}

valid_labels = {"oil_palm", "other", "uncertain"}

for patch_id in range(len(X)):
    if patch_id not in label_map:
        label_map[patch_id] = "unlabeled"

def save_labels():
    rows = []
    for i in range(len(X)):
        rows.append({
            "patch_id": i,
            "source_file": str(sources[i]),
            "label": label_map.get(i, "unlabeled")
        })

    pd.DataFrame(rows).to_csv(LABEL_FILE, index=False)

current_id = 0

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
plt.subplots_adjust(bottom=0.23)

def draw_patch():
    axes[0].clear()
    axes[1].clear()

    patch = X[current_id]

    # Channel order: B1, B2, B3, B4, ...
    # RGB display uses B4 (red), B3 (green), B2 (blue).
    rgb = np.stack(
        [patch[3], patch[2], patch[1]],
        axis=-1
    )

    axes[0].imshow(np.clip(rgb, 0, 1), interpolation="nearest")
    axes[0].set_title("RGB satellite patch")

    # NDVI is band 13, array index 12
    axes[1].imshow(
        patch[12],
        cmap="RdYlGn",
        vmin=-1,
        vmax=1,
        interpolation="nearest"
    )
    axes[1].set_title("NDVI")

    for ax in axes:
        ax.axis("off")

    current_label = label_map[current_id]

    fig.suptitle(
        f"Patch {current_id + 1}/{len(X)} | "
        f"File: {sources[current_id]}\n"
        f"Current label: {current_label}\n"
        "Keys: 1 = oil palm | 2 = other | "
        "3 = uncertain | n = next | p = previous | q = save & quit"
    )

    fig.canvas.draw_idle()

def on_key(event):
    global current_id

    if event.key == "1":
        label_map[current_id] = "oil_palm"
        save_labels()
        print(f"Patch {current_id}: oil_palm saved")

    elif event.key == "2":
        label_map[current_id] = "other"
        save_labels()
        print(f"Patch {current_id}: other saved")

    elif event.key == "3":
        label_map[current_id] = "uncertain"
        save_labels()
        print(f"Patch {current_id}: uncertain saved")

    elif event.key == "n":
        current_id = min(current_id + 1, len(X) - 1)

    elif event.key == "p":
        current_id = max(current_id - 1, 0)

    elif event.key == "q":
        save_labels()
        print(f"Labels saved to: {LABEL_FILE}")
        plt.close(fig)
        return

    draw_patch()

fig.canvas.mpl_connect("key_press_event", on_key)

draw_patch()
print("Label viewer opened.")
print("Click the image window before using keyboard shortcuts.")
print("Labels will be saved automatically.")

plt.show()
save_labels()
