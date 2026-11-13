import os
import hashlib
import tempfile
import pytest
from scripts.generate_data import generate_all

def compute_checksum(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def test_synthetic_data_reproducibility():
    """Verify that running the synthetic data generator twice with SEED=20261022 produces identical rows and checksums."""
    with tempfile.TemporaryDirectory() as dir1, tempfile.TemporaryDirectory() as dir2:
        out1 = os.path.join(dir1, "data")
        gt1 = os.path.join(dir1, "gt")
        out2 = os.path.join(dir2, "data")
        gt2 = os.path.join(dir2, "gt")

        manifest1 = generate_all(mode="starter", output_dir=out1, ground_truth_dir=gt1)
        manifest2 = generate_all(mode="starter", output_dir=out2, ground_truth_dir=gt2)

        # 1. Compare row counts
        assert manifest1 == manifest2, "Row counts between two runs with identical seed differed!"

        # 2. Compare file checksums for all CSVs
        for fname in os.listdir(out1):
            if fname.endswith(".csv"):
                p1 = os.path.join(out1, fname)
                p2 = os.path.join(out2, fname)
                cs1 = compute_checksum(p1)
                cs2 = compute_checksum(p2)
                assert cs1 == cs2, f"Checksum mismatch in {fname} between two identical runs!"
