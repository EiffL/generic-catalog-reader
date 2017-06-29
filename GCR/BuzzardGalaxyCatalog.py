"""
Buzzard galaxy catalog class.
"""
from __future__ import division
import os
import numpy as np
from astropy.io import fits
from astropy.cosmology import FlatLambdaCDM
from .BaseGalaxyCatalog import BaseGalaxyCatalog

__all__ = ['BuzzardGalaxyCatalog']


def _get_fits_data(fits_file):
    return fits_file[1].data


class BuzzardGalaxyCatalog(BaseGalaxyCatalog):
    """
    Argonne galaxy catalog class. Uses generic quantity and filter mechanisms
    defined by BaseGalaxyCatalog class.
    """

    def _subclass_init(self, catalog_dir, base_catalog_dir=os.curdir, **kwargs):

        self._pre_filter_quantities = {'original_healpixel'}

        self._quantity_modifiers = {
            'redshift': ('truth', 'Z'),
        }

        self._catalog_dir = os.path.join(base_catalog_dir, catalog_dir)
        self._catalog_subdirs = ('truth',)
        self.cosmology = FlatLambdaCDM(H0=0.7, Om0=0.286)
        self._npix = 768
        self._filename_template = 'Chinchilla-0_lensed.{}.fits'


    def _generate_native_quantity_list(self):
        native_quantities = {'original_healpixel'}
        for _, dataset in self._iter_native_dataset():
            for k, v in dataset.iteritems():
                for name in _get_fits_data(v).names:
                    native_quantities.add((k, name))
            break
        return native_quantities


    def _iter_native_dataset(self, pre_filters=None):
        for i in range(self._npix):
            if pre_filters and not all(f[0](*([i]*(len(f)-1))) for f in pre_filters):
                continue

            fp = dict()
            for subdir in self._catalog_subdirs:
                fname = os.path.join(self._catalog_dir, subdir, self._filename_template.format(i))
                try:
                    fp[subdir] = fits.open(fname)
                except (IOError, OSError):
                    pass
            try:
                if all(subdir in fp for subdir in self._catalog_subdirs):
                    yield i, fp
            finally:
                for f in fp.itervalues():
                    f.close()


    @staticmethod
    def _fetch_native_quantity(dataset, native_quantity):
        healpix, fits_data = dataset
        if native_quantity == 'original_healpixel':
            data = np.empty(_get_fits_data(fits_data.values()[0]).shape, np.int)
            data.fill(healpix)
            return data
        return _get_fits_data(fits_data[native_quantity[0]])[native_quantity[1]]

