import numpy as np
import xarray as xr
from scipy.linalg import cholesky, sqrtm


from . import utils

def gaspari_cohn(dist, loc_radius):
    '''
    Vectorized Gaspari-Cohn localization function.
    
    Args:
        dist (ndarray): Distance(s) between model state and observation.
        loc_radius (float): Localization radius (distance beyond which covariance is set to zero).

    Reference:
        Gaspari, G., Cohn, S.E., 1999. Construction of correlation functions in two and three dimensions.
        Quarterly Journal of the Royal Meteorological Society 125, 723-757. https://doi.org/10.1002/qj.49712555417
    '''
    # Normalize the distances
    r = np.abs(dist) / loc_radius
    
    # Initialize the result array with zeros
    f = np.zeros_like(r)
    
    # Eq. (4.10) in Gaaspari & Coh (1999)
    mask1 = r <= 1
    f[mask1] = -r[mask1]**5 / 4 + r[mask1]**4 / 2 + 5/8 * r[mask1]**3 - 5/3 * r[mask1]**2 + 1
    
    mask2 = (r > 1) & (r <= 2)
    f[mask2] = r[mask2]**5 / 12 - r[mask2]**4 / 2 + 5/8 * r[mask2]**3  + 5/3 * r[mask2]**2 - 5 * r[mask2] + 4 - 2/3 / r[mask2]

    f[f<0] = 0 # force f >= 0
    return f

def gaspari_cohn_dash(dist, loc_radius, scale=0.5):
    """
    Implements a Gaspari-Cohn 5th order polynomial localization function.
    
    Parameters:
        dist (ndarray): An array of distances.
        loc_radius (float): The cutoff radius, beyond which weights are zero.
        scale (float or str, optional): The length scale for the polynomial.
            Must be on the interval 0 < scale <= 0.5, or 'optimal' to use the optimal
            length scale as described by Lorenc (2003). Default is 0.5.
    
    Returns:
        weights (ndarray): Covariance localization weights with the same shape as distances.
    """
    # Set the scale if 'optimal' is specified
    if isinstance(scale, str) and scale == 'optimal':
        scale = np.sqrt(10 / 3)
    
    # Define length scale and localization radius
    c = scale * loc_radius
    
    # Preallocate weights array with ones
    weights = np.ones_like(dist)
    
    # Calculate mask arrays for the different distance ranges
    outside_radius = dist > loc_radius
    inside_scale = dist <= c
    in_between = ~inside_scale & ~outside_radius

    # Apply Gaspari-Cohn polynomial
    X = dist / c
    weights[outside_radius] = 0
    weights[in_between] = X[in_between]**5 / 12 - 0.5 * X[in_between]**4 + 0.625 * X[in_between]**3 + (5 / 3) * X[in_between]**2 - 5 * X[in_between] + 4 - 2 / (3 * X[in_between])
    weights[inside_scale] = -0.25 * X[inside_scale]**5 + 0.5 * X[inside_scale]**4 + 0.625 * X[inside_scale]**3 - (5 / 3) * X[inside_scale]**2 + 1
    
    # Ensure weights are non-negative due to rounding errors
    weights[weights < 0] = 0
    
    return weights



class EnSRF:
    def __init__(self, X=None, Y=None, y=None, R=None, L=None, Lobs=None):
        self.X = X            # ensemble of the prior state vectors (n x N)
        self.Y = Y            # ensemble of the forward estimates (m x N); Y=H(X)
        self.y = y            # observations (m x 1)
        self.R = R            # obs err matrix (m x m)
        self.L = L            # localization matrix (n x m)
        self.Lobs = Lobs      # localization matrix (m x m)

    def update(self, debug=False):
        ''' Perform an EnSRF update with localization. '''
        N = self.X.shape[1]  # Ensemble size

        # Compute the ensemble mean
        Xm = np.mean(self.X, axis=1, keepdims=True)
        Xp = self.X - Xm

        Ym = np.mean(self.Y, axis=1, keepdims=True)
        Yp = self.Y - Ym

        # Observation error covariance matrix
        Ycov = (Yp @ Yp.T) / (N - 1)

        # Localize the obs err covariance matrix
        if self.Lobs is not None:
            Ycov_loc = Ycov * self.Lobs
        else:
            Ycov_loc = Ycov

        C =  Ycov_loc + self.R

        # Kalman gain matrix
        XYcov = (Xp @ Yp.T) / (N - 1)

        # Localize the Kalman gain
        if self.L is not None:
            XYcov_loc = XYcov * self.L
        else:
            XYcov_loc = XYcov

        K = XYcov_loc @ np.linalg.inv(C)

        # Observation innovation
        d = self.y - Ym

        # Update the ensemble mean
        Xm_updated = Xm + K @ d

        # Update the ensemble perturbations
        T = np.eye(N) - (Yp.T @ np.linalg.inv(C)) @ Yp / (N - 1)
        Xp_updated = Xp @ T

        # Combine updated mean and perturbations
        self.X_updated = Xm_updated + Xp_updated

        if debug:
            self.Xm = Xm
            self.Xp = Xp
            self.Ym = Ym
            self.Yp = Yp
            self.C = C
            self.K = K
            self.d = d
            self.T = T

class EnSRF_DASH:
    def __init__(self, X=None, Y=None, y=None, R=None, L=None, Lobs=None):
        self.X = X            # ensemble of the prior state vectors (n x N)
        self.Y = Y            # ensemble of the forward estimates (m x N); Y=H(X)
        self.y = y            # observations (m x 1)
        self.R = R            # obs err matrix (m x m)
        self.L = L            # localization matrix (n x m)
        self.Lobs = Lobs      # localization matrix (m x m)

    def update(self, debug=False):
        ''' Perform an EnSRF update with localization. '''
        N = self.X.shape[1]  # Ensemble size

        # Compute the ensemble mean
        Xm = np.mean(self.X, axis=1, keepdims=True)
        Xp = self.X - Xm

        Ym = np.mean(self.Y, axis=1, keepdims=True)
        Yp = self.Y - Ym

        # Observation error covariance matrix
        Ycov = (Yp @ Yp.T) / (N - 1)

        # Localize the obs err covariance matrix
        if self.Lobs is not None:
            Ycov_loc = self.Lobs * Ycov
        else:
            Ycov_loc = Ycov

        C =  Ycov_loc + self.R

        # Kalman gain matrix
        XYcov = (Xp @ Yp.T) / (N - 1)

        # Localize the Kalman gain
        if self.L is not None:
            XYcov_loc = self.L * XYcov
        else:
            XYcov_loc = XYcov

        K = XYcov_loc @ np.linalg.inv(C)

        # Observation innovation
        d = self.y - Ym

        # Update the ensemble mean
        Xm_updated = Xm + K @ d

        # Update the ensemble perturbations
        Ksqrt = sqrtm(C)
        Ksqrt_inv_transpose = np.linalg.inv(Ksqrt).T
        Rcov_sqrt = sqrtm(self.R)
        Ka = K @ Ksqrt_inv_transpose @ np.linalg.inv(Ksqrt + Rcov_sqrt)
        Xp_updated = Xp - Ka @ Yp

        # Combine updated mean and perturbations
        self.X_updated = Xm_updated + Xp_updated

        if debug:
            self.Xm = Xm
            self.Xp = Xp
            self.Ym = Ym
            self.Yp = Yp
            self.C = C
            self.K = K
            self.d = d


class EnOI:
    def __init__(self, X_target=None, X=None, Y=None, y=None, R=None, L=None):
        self.X_target = X_target   # the **monthly** prior state vectors (n x 1)
        self.X = X         # ensemble of the prior state vectors (n x N)
        self.Y = Y         # ensemble of the forward estimates (m x N); Y=H(X)
        self.y = y         # observations (m x 1)
        self.R = R         # obs err matrix (m x m)
        self.L = L         # localization matrix (n x m)

    def update(self, debug=False):
        ''' Perform an EnOI update with localization. '''
        N = self.X.shape[1]  # Ensemble size

        # Compute the ensemble mean
        Xm = np.mean(self.X, axis=1, keepdims=True)
        Xp = self.X - Xm

        Ym = np.mean(self.Y, axis=1, keepdims=True)
        Yp = self.Y - Ym

        # Observation error covariance matrix
        C = (Yp @ Yp.T) / (N - 1) + self.R

        # Kalman gain matrix
        K = (Xp @ Yp.T) / (N - 1) @ np.linalg.inv(C)

        # Localize the Kalman gain
        if self.L is not None:
            K_loc = K * self.L
        else:
            K_loc = K

        # Observation innovation
        d = self.y - Ym

        # the increment
        inc = K_loc @ d

        # update
        self.X_target_updated = self.X_target + inc

        if debug:
            self.Xm = Xm
            self.Xp = Xp
            self.Ym = Ym
            self.Yp = Yp
            self.C = C
            self.K = K
            self.K_loc = K_loc
            self.d = d


class Solver:
    def __init__(self, prior=None, obs=None, prior_target=None):
        self.prior = prior.copy() if prior is not None else None
        self.obs = obs.copy() if obs is not None else None
        self.prior_target = prior_target.copy() if prior_target is not None else None

    def prep(self, localize=True, loc_radius=2500, dist_vsf=1, dlat=1, dlon=1, loc_method='dash',
             recon_season=list(range(1, 13)), startover=False, nearest_valid_radius=5, **fwd_kws):
        ''' Prepare Y=H(X) and the localization matrix for DA

        Args:
            dist_vsf (float, list of float): the vertical scaling factor of the distance

        '''
        if not hasattr(self.prior, 'ds_rgd'):
            utils.p_header(f'>>> Regridding the prior (dlat={dlat}, dlon={dlon})')
            self.prior.regrid(dlat=dlat, dlon=dlon)

        if startover or not hasattr(self.prior, 'Y'):
            utils.p_header('>>> Proxy System Modeling: Y = H(X)')
            self.prior.get_Y(self.obs, nearest_valid_radius=nearest_valid_radius, **fwd_kws)

        if not hasattr(self.prior, 'ds_ann'):
            utils.p_header(f'>>> Annualizing prior w/ season: {recon_season}')
            self.prior.annualize(months=recon_season)

        if localize and not hasattr(self.prior, 'dist'):
            loc_func = {
                'cpda': gaspari_cohn,
                'dash': gaspari_cohn_dash,
            }
            utils.p_header('>>> Computing the localization matrix')
            self.prior.get_dist(self.prior.obs_assim, dist_vsf)
            self.L = loc_func[loc_method](self.prior.dist, loc_radius)
            self.obs.get_dist()
            self.Lobs = loc_func[loc_method](self.obs.dist, loc_radius)
        else:
            self.L = None
            self.Lobs = None

    def run(self, method='EnSRF', debug=False):
        algo = {
            'EnSRF': EnSRF,
            'EnSRF_DASH': EnSRF_DASH,
            'EnOI': EnOI,
        }

        kws = {}
        for m in algo.keys():
            kws[m] = {
                'X': self.prior.X,
                'Y': self.prior.Y,
                'y': self.obs.y,
                'R': self.obs.R,
                'L': self.L,
                'Lobs': self.Lobs,
            }

        if self.prior_target is not None:
            kws['EnOI']['X_target'] = self.prior_target.X

        self.S = algo[method](**kws[method])

        utils.p_header('>>> DA update')
        self.S.update(debug=debug)

        utils.p_header('>>> Formatting the posterior')
        if method in ['EnSRF', 'EnSRF_DASH']:
            self.post = utils.states2ds(self.S.X_updated, self.prior.ds_ann)
        elif method == 'EnOI':
            self.post = utils.states2ds(self.S.X_target_updated, self.prior_target.ds_ann)