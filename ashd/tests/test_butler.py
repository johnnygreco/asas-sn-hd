from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ashd.butler import Butler

def test_butler():
    ra = '02h39m59.3s'
    dec = '-34d26m57s'
    b = Butler()
    fn = b.get_image_fn(ra, dec, unit=('hourangle', 'degree'))
    assert fn
    data = b.get_data(fn=fn)
    assert data.shape == (2048, 2048)
