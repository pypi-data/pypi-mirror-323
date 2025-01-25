import tifffile
from cellstitch_cuda.pipeline import cellstitch_cuda
from cellstitch_cuda.interpolate import full_interpolate
from cellstitch_cuda.interpolate_cupy import full_interpolate as interpolate_new

# img = r"E:\1_DATA\Rheenen\tvl_jr\3d stitching\raw4-small\raw.tif"
#
# cellstitch_cuda(img, output_masks=True, verbose=True, seg_mode="nuclei_cells", n_jobs=-1)

masks = tifffile.imread(r"E:\1_DATA\Rheenen\tvl_jr\3d stitching\raw4-small\cellstitch_masks.tif")

import time

time_start = time.time()
masks = full_interpolate(masks, anisotropy=4, n_jobs=-1, verbose=True)
print("Time to interpolate: ", time.time() - time_start)

# tifffile.imwrite(r"E:\1_DATA\Rheenen\tvl_jr\3d stitching\raw4-large\cellstitch_masks_interpolated.tif", masks)
