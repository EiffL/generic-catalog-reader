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
            'galaxy_id': ('truth', 'ID'),
            'redshift_true': ('truth', 'Z'),
            'ra': ('truth', 'RA'),
            'dec': ('truth', 'DEC'),
            'ra_true': ('truth', 'TRA'),
            'dec_true': ('truth', 'TDEC'),
            'halo_id': ('truth', 'HALOID'),
            'is_bcg': (lambda x: x.astype(np.bool), ('truth', 'CENTRAL')),
            'ellipticity_1': ('truth', 'EPSILON', 0),
            'ellipticity_2': ('truth', 'EPSILON', 1),
            'ellipticity_1_true': ('truth', 'TE', 0),
            'ellipticity_2_true': ('truth', 'TE', 1),
            'size': ('truth', 'SIZE'),
            'size_true': ('truth', 'TSIZE'),
            'shear_1': ('truth', 'GAMMA1'),
            'shear_2': ('truth', 'GAMMA2'),
            'convergence': ('truth', 'KAPPA'),
            'magnification': ('truth', 'MU'),
            'position_x': ('truth', 'PX'),
            'position_y': ('truth', 'PY'),
            'position_z': ('truth', 'PZ'),
            'velocity_x': ('truth', 'VX'),
            'velocity_y': ('truth', 'VY'),
            'velocity_z': ('truth', 'VZ'),
        }

        for i, b in enumerate('grizY'):
            self._quantity_modifiers['Mag01_true_{}_des'.format(b)] = ('truth', 'AMAG', i)
            self._quantity_modifiers['Mag01_true_{}_any'.format(b)] = ('truth', 'AMAG', i)
            self._quantity_modifiers['mag_{}_des'.format(b)] = ('truth', 'OMAG', i)
            self._quantity_modifiers['mag_{}_any'.format(b)] = ('truth', 'OMAG', i)
            self._quantity_modifiers['magerr_{}_des'.format(b)] = ('truth', 'OMAGERR', i)
            self._quantity_modifiers['magerr_{}_any'.format(b)] = ('truth', 'OMAGERR', i)


        self._catalog_dir = os.path.join(base_catalog_dir, catalog_dir)
        self._catalog_subdirs = ('truth',)
        self.cosmology = FlatLambdaCDM(H0=0.7, Om0=0.286)
        self._npix = 768
        self._filename_template = 'Chinchilla-0_lensed.{}.fits'


    def _generate_native_quantity_list(self):
        native_quantities = {'original_healpixel'}
        for _, dataset in self._iter_native_dataset():
            for k, v in dataset.iteritems():
                fields = _get_fits_data(v).dtype.fields
                for name, (dt, size) in _get_fits_data(v).dtype.fields.items():
                    if dt.shape:
                        for i in range(dt.shape[0]):
                            native_quantities.add((k, name, i))
                    else:
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
        data =  _get_fits_data(fits_data[native_quantity[0]])[native_quantity[1]]
        if len(native_quantity) == 3:
            data = data[:,native_quantity[2]]
        return data
