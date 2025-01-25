# microtiff
A Python module and CLI tool for converting proprietary microscopy formats to TIFF with JSON metadata sidecar files.

## Supported data types
Both supported modules and modules working with errata are listed below.

| Sensor | Status | Errata/Notes |
| --- | --- | --- |
| Imaging FlowCytobot/IFCB (.adc, .hdr, .roi) | :white_check_mark: | |
| LISST-Holo (.pgm) | :white_check_mark: | Only extracts raw interference field, does not reconstruct images. Metadata export broken. |
| LISST-Holo2 (.pgm) | :white_check_mark: | See above |
| FlowCam | :x: | In active development |

## Dependencies

- pillow
- numpy
- holopy (for LISST-Holo/LISST-Holo2 "construct" mode only)
    - xarray
    - h5netcdf
    - nose
    - matplotlib
    - h5py
    - pyYaml
    - scipy
    - imp

For essential dependencies you can use the following command:
`$ pip install pillow numpy`

HoloPy is not avaliaiable via PIP. If you are using anaconda, you may install it there. Alternatively, install from source by following instructions at [https://holopy.readthedocs.io/en/master/tutorial/dev_tutorial.html](https://holopy.readthedocs.io/en/master/tutorial/dev_tutorial.html#dev-install). Alternatively, use the install script at [scripts/install-holopy.sh](scripts/install-holopy.sh)

## Acknowledgements
This library is comprised of work from various researchers, some of whom are not direct contributors to this repository.

The LISST-Holo decoder is based on work by [Sari Giering](https://github.com/sarigiering), [Will Major](https://github.com/obg-wrm) and [Mojtaba Masoudi](https://github.com/Mojtabamsd)
