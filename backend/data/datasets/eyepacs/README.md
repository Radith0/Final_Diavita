# EyePACS Diabetic Retinopathy Dataset

This directory is configured for the EyePACS diabetic retinopathy detection dataset.

## Dataset Structure

The dataset files are large and need to be extracted separately. The expected structure is:

```
eyepacs/
├── train/              # Training images (extracted from train.zip.001-005)
├── test/               # Test images (extracted from test.zip.001-007)
├── trainLabels.csv     # Training labels (extracted from trainLabels.csv.zip)
└── sampleSubmission.csv # Sample submission format (extracted from sampleSubmission.csv.zip)
```

## Source Files

The dataset typically comes in these compressed files:
- `train.zip.001` through `train.zip.005` - Training images (multi-part archive)
- `test.zip.001` through `test.zip.007` - Test images (multi-part archive)
- `trainLabels.csv.zip` - Labels for training images
- `sampleSubmission.csv.zip` - Sample submission format

## Extraction Instructions

If you have the dataset files, extract them using:

### Install p7zip (if not already installed)
```bash
sudo apt install p7zip-full -y
```

### Extract training images
```bash
7z x train.zip.001 -o./train
```

### Extract test images
```bash
7z x test.zip.001 -o./test
```

### Extract CSV files
```bash
unzip trainLabels.csv.zip -d .
unzip sampleSubmission.csv.zip -d .
```

## Dataset Information

- **Source**: Kaggle - Diabetic Retinopathy Detection Competition
- **Images**: High-resolution retina images taken under various imaging conditions
- **Labels**: 5 severity levels (0-4)
  - 0: No DR
  - 1: Mild
  - 2: Moderate
  - 3: Severe
  - 4: Proliferative DR

## Notes

- The dataset is very large (several GB)
- Training images: ~35,000 images
- Test images: ~53,000 images
- Due to size constraints, the dataset files are not stored in this repository
- The notebook is configured to work with this directory structure once extracted
