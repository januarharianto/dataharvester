"""
This script downloads the National Digital Elevation Model (DEM) 1 Second Hydrologically Enforced product,
derived from the National DEM SRTM 1 Second and National Watercourses, lakes and Reservoirs.
The output image is a geotiff file with a user defined resolution and bbox.
This script also includes the capabilities to generate slope and aspect from the extracted DEM.

Core functions:
    get_capabilities(): get the available layers and their metadata
    getwcs_dem(): download the data as geotiff file for given bbox and resolution
    dem2slope(): convert geotiff to slope raster
    dem2aspect(): convert geotiff to aspect raster
    getdict_license(): get the license and attributes for the DEM 1 arc second grid

The DEM layer metadata can be retrieved with the function get_capabilities().
and the respective licensing and attribution are availabe with the module function getdict_license()

To download the DEM data, the function getwcs_dem() is used.

For more details about the data, see:
https://ecat.ga.gov.au/geonetwork/srv/eng/catalog.search#/metadata/72759

WCS url:
https://services.ga.gov.au/site_9/services/DEM_SRTM_1Second_Hydro_Enforced/MapServer/WCSServer?request=GetCapabilities&service=WCS

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan
"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
from datetime import datetime, timezone
try:
    from osgeo import gdal
except ImportError:
    import gdal


def get_metadict():
    """
    Get dictionary of meta data

    OUTPUT:
    layerdict : dict
        dictionary of meta data
    """
    demdict = {}
    demdict['title'] = 'DEM 1 Second Grid'
    demdict['description'] = 'Digital Elevation Model (DEM) of Australia derived from STRM with 1 Second Grid - Hydrologically Enforced.'
    demdict['crs'] = 'EPSG:4326'
    demdict['bbox'] = [112.99986111100009, -44.0001388895483, 153.9998611116614, -10.000138888999906]
    demdict['resolution_arcsec'] = 1
    return demdict

def getdict_license():
    """
    Retrieves the Geoscience Australia data license for the DEM Web Map Service as dict
    """
    dict = {
        "name": "Digital Elevation Model (DEM) of Australia derived from STRM with 1 Second Grid - Hydrologically Enforced",
        "source_url": "https://www.clw.csiro.au/aclep/soilandlandscapegrid/ProductDetails.html",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© Copyright 2017-2022, Geoscience Australia",
        "attribution": "Commonwealth of Australia (Geoscience Australia) ",
        }
    return dict

def get_capabilities(url):
    """
    Get capabilities from WCS layer.

    Parameters
    ----------
    url : str
        layer url

    Returns
    -------
    keys    : list
        layer identifiers
    titles  : list  of str
        layer titles
    descriptions : list of str
        layer descriptions
    bboxs   : list of floats
        layer bounding boxes
    """

     # Create WCS object
    wcs = WebCoverageService(url, version='1.0.0', timeout=300)

    # Get coverages and content dict keys
    content = wcs.contents
    keys = content.keys()

    print('Following data layers are available:')
    title_list = []
    description_list = []
    bbox_list = []
    for key in keys:
        print(f'key: {key}')
        print(f'title: {wcs[key].title}')
        title_list.append(wcs[key].title)
        print(f'{wcs[key].abstract}')
        description_list.append(wcs[key].abstract)
        print(f'bounding box: {wcs[key].boundingBoxWGS84}')
        bbox_list.append(wcs[key].boundingBoxWGS84)
        print('')

    return keys, title_list, description_list, bbox_list


def getwcs_dem(outpath, bbox, resolution = 1,
    url = 'https://services.ga.gov.au/site_9/services/DEM_SRTM_1Second_Hydro_Enforced/MapServer/WCSServer?request=GetCapabilities&service=WCS',
    crs = 'EPSG:4326'):
    """
    Main function to download and save geotiff from WCS layer.
    Default downloads the DEM 1 arc second grid from Geoscience Australia using the folllwing WCS url:
    Url = https://services.ga.gov.au/site_9/services/DEM_SRTM_1Second_Hydro_Enforced/MapServer/WCSServer?request=GetCapabilities&service=WCS

    Parameters
    ----------
    outpath : str
        output directory for the downloaded file
    bbox : list
        layer bounding box
    resolution : int
        layer resolution in arcsec (default 1)
    url : str
        url of wcs server, default is the Geoscience Australia DEM 1 arc second grid
    crs: str
        crs default 'EPSG:4326'

    Return
    ------
    Output filename
    """
    # Convert resolution into width and height pixel number
    # width = abs(bbox[2] - bbox[0])
    # height = abs(bbox[3] - bbox[1])
    # nwidth = int(width / resolution * 3600)
    # nheight = int(height / resolution * 3600)

    # If the resolution passed is None, set to native resolution of datasource
    if resolution is None:
        resolution = get_metadict()['resolution_arcsec']

    os.makedirs(outpath, exist_ok=True)
    # Create WCS object and get data
    try:
        wcs = WebCoverageService(url, version='1.0.0', timeout= 300)
        layername = wcs['1'].title
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        fname_out = layername.replace(' ', '_') + '_' + date + '.tif'
        outfname = os.path.join(outpath, fname_out)
        if os.path.exists(outfname):
            print(f'{outfname} already exists')
        else:
            data = wcs.getCoverage(identifier = '1',
                bbox=bbox,
                format='GeoTIFF',
                crs=crs,
                resx=resolution / 3600,
                resy=resolution / 3600,
                Styles='tc'
                )
            # Save data to file
            with open(outfname, 'wb') as f:
                f.write(data.read())
            print("DEM downloaded to:", outfname)
    except:
        print('Download failed')
        return False
    return outfname


def plot_raster(infname):
    """
    Read in raster tif with rasterio and visualise as map

    Parameters
    ----------
    infname : str
    """
    data = rasterio.open(infname)
    # show image
    show(data)



def dem2slope(fname_dem):
    """
    Calculate slope from DEM and save as geotiff

    Parameters
    ----------
    fname_dem : str
        DEM path + file name
    """
    # Get filename
    fname = os.path.basename(fname_dem)
    # Get path for output
    path = os.path.dirname(fname_dem)
    fname_out = os.path.join(path,'Slope_' + fname)
    gdal.DEMProcessing(fname_out , fname_dem, 'slope')
    print("DEM slope from:", fname_dem, " saved to:", fname_out)
    return fname_out

def dem2aspect(fname_dem):
    """
    Calculate aspect from DEM and save as geotiff

    Parameters
    ----------
    fname_dem : str
        DEM file name
    """
    # Get filename
    fname = os.path.basename(fname_dem)
    # Get path for output
    path = os.path.dirname(fname_dem)
    fname_out = os.path.join(path,'Aspect_' + fname)
    gdal.DEMProcessing(fname_out , fname_dem, 'aspect')
    print("DEM aspect from:", fname_dem, " saved to:", fname_out)
    return fname_out


def test_getwcs_dem(outpath = './test_DEM/'):
    """
    Test script
    """
    bbox = (114, -44, 153.9, -11)
    resolution = 100
    url = 'https://services.ga.gov.au/site_9/services/DEM_SRTM_1Second_Hydro_Enforced/MapServer/WCSServer?request=GetCapabilities&service=WCS'
    crs = 'EPSG:4326'
    # get capabilities
    keys, title_list, description_list, bbox_list = get_capabilities(url)
    # get data
    print('Retrieving data from Geoscience Australia DEM 1 arc second grid...')
    outfname = getwcs_dem(outpath, bbox, resolution, url, crs)
    # Convert to slope and aspect
    print('Convert to slope and aspect...')
    dem2slope(outfname)
    dem2aspect(outfname)
    # plot DEM
    plot_raster(outfname)