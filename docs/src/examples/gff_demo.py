# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: cytodataframe-shAZamSV-py3.12
#     language: python
#     name: python3
# ---

import pathlib
import pandas as pd
from cytodataframe import CytoDataFrame


profiles = str(pathlib.Path(
    "~/mnt/bandicoot/NF1_organoid_data/data/NF0018_T6/2D_analysis/3.converted/middle_slice_sc.parquet"
    ).expanduser())
images_dir = str(pathlib.Path(
    "~/mnt/bandicoot/NF1_organoid_data/data/NF0018_T6/2D_analysis/0c.middle_n_slice_max_proj"
    ).expanduser())


# +
# Keep notebook execution fast by default. Set to None to use all rows.
max_rows_for_demo = 2000

base_df = pd.read_parquet(profiles)
if max_rows_for_demo is not None:
    base_df = base_df.head(max_rows_for_demo).copy()

bounding_box_cols = [
    'Cytoplasm_AreaShape_BoundingBoxArea',
    'Cytoplasm_AreaShape_BoundingBoxMaximum_X',
    'Cytoplasm_AreaShape_BoundingBoxMaximum_Y',
    'Cytoplasm_AreaShape_BoundingBoxMinimum_X',
    'Cytoplasm_AreaShape_BoundingBoxMinimum_Y',
    'Cells_AreaShape_BoundingBoxArea',
    'Cells_AreaShape_BoundingBoxMaximum_X',
    'Cells_AreaShape_BoundingBoxMaximum_Y',
    'Cells_AreaShape_BoundingBoxMinimum_X',
    'Cells_AreaShape_BoundingBoxMinimum_Y',
    'Nuclei_AreaShape_BoundingBoxArea',
    'Nuclei_AreaShape_BoundingBoxMaximum_X',
    'Nuclei_AreaShape_BoundingBoxMaximum_Y',
    'Nuclei_AreaShape_BoundingBoxMinimum_X',
    'Nuclei_AreaShape_BoundingBoxMinimum_Y',
]

linked_df = base_df.copy()
img_cols = [c for c in linked_df.columns if c.startswith("Image_FileName_")]

# Finicky bit #1: profile filenames end with '_illumcorrect.tiff',
# but files on disk are named without that suffix and use '.tif'.
linked_df[img_cols] = (
    linked_df[img_cols]
    .apply(lambda s: s.str.replace("_illumcorrect", "", regex=False))
    .apply(lambda s: s.str.replace(".tiff", ".tif", regex=False))
)

# Finicky bit #2: each image lives in a subfolder named by the well/site
# prefix before the first underscore (e.g., 'D11-3_555.tif' -> folder 'D11-3').
path_cols = {c: c.replace("FileName", "PathName") for c in img_cols}

# Compute the per-row folder once, then reuse for every Image_PathName_* column.
well_dir = linked_df[img_cols[0]].str.split("_").str[0].map(
    lambda well: str(pathlib.Path(images_dir) / well)
)
image_path_df = pd.DataFrame(
    {path_col: well_dir for path_col in path_cols.values()},
    index=linked_df.index,
)

df = CytoDataFrame(
    data=linked_df,
    data_image_paths=image_path_df,
    data_mask_context_dir=images_dir,
    data_bounding_box=linked_df[bounding_box_cols],
)

print(f"Rows loaded for notebook demo: {len(df):,}")
pd.concat([df[img_cols], image_path_df], axis=1).head()

# -

filename_cols = [col for col in df.columns.tolist() if "file" in col.lower()]
df[filename_cols].head()

