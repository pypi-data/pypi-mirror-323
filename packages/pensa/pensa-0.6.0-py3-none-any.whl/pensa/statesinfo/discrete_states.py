import warnings
import numpy as np
from queue import PriorityQueue
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import argrelextrema
import os
from pensa.features import \
    correct_angle_periodicity, \
    correct_spher_angle_periodicity
import itertools
from multiprocessing import Pool
from functools import partial


# -- Functions to cluster feature distributions into discrete states --


def _smooth(x, window_len, window=None):
    """
    Smooth data so that true extrema can be found without any noise


    Parameters
    ----------
    x : list
        Distribution to be smoothed.
    window_len : int
        number of bins to smooth over.
    window : str, optional
        Type of window to use for the smoothing. The default is None=Hanning.

    Raises
    ------
    ValueError
        If window argument is not recognised.

    Returns
    -------
    list
        Smoothed distribution.

    """
    if window is None:
        window_type = 'hanning'
    if x.ndim != 1:
        raise ValueError
    if x.size < window_len:
        raise ValueError
    if window_len < 3:
        return x
    if window_type not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError
    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    if window_type == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window_type + '(window_len)')
    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


def _find_nearest(distr, value):
    """
    Find the nearest value in a distribution to an arbitrary reference value.

    Parameters
    ----------
    distr : list
        The distribution to locate a certain point within.
    value : float
        Reference value for locating within the distribution.

    Returns
    -------
    float
        Closest value to reference value in distribution.

    """
    array = np.array(distr)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def _printKclosest(arr, n, x, k):
    """
    Print K closest values to a specified value.

    Parameters
    ----------
    arr : list
        The distribution of values.
    n : int
        Search through the first n values of arr for k closest values.
    x : float
        The reference value for which the closest values are sought.
    k : int
        Number of closest values desired.

    Returns
    -------
    a : list
        The closest k values to x.

    """
    a = []
    # Make a max heap of difference with
    # first k elements.
    pq = PriorityQueue()
    for neighb in range(k):
        pq.put((-abs(arr[neighb] - x), neighb))
    # Now process remaining elements
    for neighb in range(k, n):
        diff = abs(arr[neighb] - x)
        p, pi = pq.get()
        curr = -p
        # If difference with current
        # element is more than root,
        # then put it back.
        if diff > curr:
            pq.put((-curr, pi))
            continue
        else:
            # Else remove root and insert
            pq.put((-diff, neighb))
    # Print contents of heap.
    while (not pq.empty()):
        p, q = pq.get()
        a.append(str("{} ".format(arr[q])))
    return a


def _gauss(x, x0, sigma, a):
    """
    Create a Gaussian distribution for a given x-axis linsapce and Gaussian parameters.

    Parameters
    ----------
    x : list
        x-axis distribution.
    x0 : float
        Mean x-value for Gaussian.
    sigma : float
        Gaussian sigma, related to FWHM.
    a : float
        Gaussian amplitude.

    Returns
    -------
    gaussian : list
        y-axis Gaussian distribution over the x-axis space.

    """

    if sigma != 0:
        gaussian = abs(a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)))
    return gaussian


def _bimodal(x, mu1, sigma1, A1, mu2, sigma2, A2):
    """
    Two Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    return _distribution


def _trimodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
              mu3, sigma3, A3):
    """
    Three Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    return _distribution


def _quadmodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4):
    """
    Four Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    return _distribution


def _quinmodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4,
               mu5, sigma5, A5):
    """
    Five Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    return _distribution


def _sexmodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
              mu3, sigma3, A3, mu4, sigma4, A4,
              mu5, sigma5, A5, mu6, sigma6, A6):
    """
    Six Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    _distribution += _gauss(x, mu6, sigma6, A6)
    return _distribution


def _septmodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4,
               mu5, sigma5, A5, mu6, sigma6, A6,
               mu7, sigma7, A7):
    """
    Seven Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    _distribution += _gauss(x, mu6, sigma6, A6)
    _distribution += _gauss(x, mu7, sigma7, A7)
    return _distribution


def _octomodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4,
               mu5, sigma5, A5, mu6, sigma6, A6,
               mu7, sigma7, A7, mu8, sigma8, A8):
    """
    Eight Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    _distribution += _gauss(x, mu6, sigma6, A6)
    _distribution += _gauss(x, mu7, sigma7, A7)
    _distribution += _gauss(x, mu8, sigma8, A8)
    return _distribution


def _nonamodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4,
               mu5, sigma5, A5, mu6, sigma6, A6,
               mu7, sigma7, A7, mu8, sigma8, A8,
               mu9, sigma9, A9):
    """
    Nine Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    _distribution += _gauss(x, mu6, sigma6, A6)
    _distribution += _gauss(x, mu7, sigma7, A7)
    _distribution += _gauss(x, mu8, sigma8, A8)
    _distribution += _gauss(x, mu9, sigma9, A9)
    return _distribution


def _decamodal(x, mu1, sigma1, A1, mu2, sigma2, A2,
               mu3, sigma3, A3, mu4, sigma4, A4,
               mu5, sigma5, A5, mu6, sigma6, A6,
               mu7, sigma7, A7, mu8, sigma8, A8,
               mu9, sigma9, A9, mu10, sigma10, A10):
    """
    Ten Gaussians
    """
    _distribution = _gauss(x, mu1, sigma1, A1)
    _distribution += _gauss(x, mu2, sigma2, A2)
    _distribution += _gauss(x, mu3, sigma3, A3)
    _distribution += _gauss(x, mu4, sigma4, A4)
    _distribution += _gauss(x, mu5, sigma5, A5)
    _distribution += _gauss(x, mu6, sigma6, A6)
    _distribution += _gauss(x, mu7, sigma7, A7)
    _distribution += _gauss(x, mu8, sigma8, A8)
    _distribution += _gauss(x, mu9, sigma9, A9)
    _distribution += _gauss(x, mu10, sigma10, A10)
    return _distribution


def _integral(x, mu, sigma, A):
    """
    Gaussian integral for evaluating state probabilities. Integration between
    negative infinity and x.

    Parameters
    ----------
    x : float
        Upper limit for integral.
    mu : float
        Gaussian mean.
    sigma : float
        Gaussian sigma.
    A : float
        Gaussian amplitude.

    Returns
    -------
    integral : float
        Area under Gaussian from negative infinity to x.

    """
    integral = (A / 2) * (1 + math.erf((x - mu) / (sigma * np.sqrt(2))))
    return integral


def _gauss_fit(distribution, traj1_len, gauss_bin, gauss_smooth):
    """
    Obtaining the gaussians to fit the distribution into a Gaussian mix.
    Bin number is chosen based on 3 degree resolution (120 bins for 360 degrees)

    Parameters
    ----------
    distribution : list
        Distribution of interest for the fitting.
    gauss_bin : int
        Bin the distribution into gauss_bin bins.
    gauss_smooth : int
        Smooth the distribution according to a Hanning window length of gauss_smooth.

    Returns
    -------
    gaussians : list
        y-axis values for the Gaussian distribution.
    xline : list
        x-axis values for the Gaussian distribution.

    """

    distr1 = distribution[:traj1_len]
    distr2 = distribution[traj1_len:]

    histox = np.histogram(distribution, bins=gauss_bin, density=True)[1]
    histo1 = np.histogram(distr1, bins=gauss_bin, range=(min(histox), max(histox)), density=True)[0]
    histo2 = np.histogram(distr2, bins=gauss_bin, range=(min(histox), max(histox)), density=True)[0]

    combined_histo = [(height1 + height2) / 2 for height1, height2 in zip(histo1, histo2)]

    distributionx = _smooth(histox[0:-1], gauss_smooth)
    # Setting histrogram minimum to zero with uniform linear shift (for noisey distributions)
    distributiony = _smooth(combined_histo - min(combined_histo), gauss_smooth)

    maxima = [distributiony[item] for item in argrelextrema(distributiony, np.greater)][0]
    # Obtain Gaussian guess params
    mean_pop = []
    sigma_pop = []
    num_closest_neighb = 28
    # Locate sigma from FWHM for each maxima
    sig_vals = []
    for extrema in maxima:
        # Find the closest values to half maximum
        closest_yvals = _printKclosest(distributiony, len(distributiony), extrema * 0.5, num_closest_neighb)
        closest_xvals = [np.where(distributiony == float(closesty))[0][0] for closesty in closest_yvals]

        mean_xval = distributionx[np.where(distributiony == extrema)[0][0]]
        half_max_xval = _find_nearest(distributionx[closest_xvals], mean_xval)

        FWHM = np.absolute(half_max_xval - mean_xval)
        sigma = FWHM / (2 * (np.sqrt(2 * np.log(2))))
        sig_vals.append(sigma)

    # The mean x of the gaussian is the value of x at the peak of y
    mean_vals = [distributionx[np.where(distributiony == extrema)[0][0]] for extrema in maxima]
    for extr_num in range(len(maxima)):
        mean_pop.append(mean_vals[extr_num])
        sigma_pop.append(sig_vals[extr_num])

    # x is the space of angles
    Gauss_xvals = np.linspace(min(distribution), max(distribution), 10000)
    # choosing the fitting mode
    peak_number = [_gauss, _bimodal, _trimodal, _quadmodal, _quinmodal,
                   _sexmodal, _septmodal, _octomodal, _nonamodal, _decamodal]
    mode = peak_number[len(sig_vals) - 1]
    expected = []

    for param_num in range(len(mean_pop)):
        expected.append(mean_pop[param_num])
        expected.append(sigma_pop[param_num])
        expected.append(maxima[param_num])

    params, cov = curve_fit(mode, distributionx, distributiony, expected, maxfev=1000000)

    gaussians = []
    gauss_num_space = np.linspace(0, (len(params)) - 3, int(len(params) / 3))

    for gauss_index in gauss_num_space:
        intmax = _integral(max(distribution),
                           params[0 + int(gauss_index)],
                           params[1 + int(gauss_index)],
                           params[2 + int(gauss_index)])

        intmin = _integral(min(distribution),
                           params[0 + int(gauss_index)],
                           params[1 + int(gauss_index)],
                           params[2 + int(gauss_index)])

        if np.abs(intmax - intmin) > 0.02:
            gaussians.append(_gauss(Gauss_xvals,
                                    params[0 + int(gauss_index)],
                                    params[1 + int(gauss_index)],
                                    params[2 + int(gauss_index)]))

    return gaussians, Gauss_xvals


def smart_gauss_fit(distr, traj1_len, gauss_bins=180, gauss_smooth=None, write_name=None):
    """
    Obtaining the gaussians to fit the distribution into a Gaussian mix.
    Bin number automatically adjusted if the Gaussian fit experiences errors.

    Parameters
    ----------
    distr : list
        Distribution of interest for the fitting.
    gauss_bins : int, optional
        Bin the distribution into gauss_bin bins. The default is 180.
    gauss_smooth : int, optional
        Smooth the distribution according to a Hanning window length of gauss_smooth.
        The default is ~10% of gauss_bins.
    write_name : str, optional
        Used in warning to notify which feature has had binning altered during clustering.
        The default is None.

    Returns
    -------
    gaussians : list
        y-axis values for the Gaussian distribution.
    xline : list
        x-axis values for the Gaussian distribution.

    """

    smooth_origin = gauss_smooth
    bin_origin = gauss_bins
    if gauss_smooth is None:
        gauss_smooth = int(gauss_bins * 0.10)

    trial = 0
    attempt_no = 0

    # making a list of +/- values for bin trials to ensure minimal change
    bin_adjust_up = np.array(range(1, 10000))
    bin_adjust_down = -bin_adjust_up.copy()
    bin_adjust = np.insert(bin_adjust_up, np.arange(len(bin_adjust_down)), bin_adjust_down)

    # if clustering does not work for a given bin number then adjust the bin number
    while trial < 1:
        try:
            gaussians, Gauss_xvals = _gauss_fit(distr, traj1_len, gauss_bins, gauss_smooth)
            trial += 1
        except Exception:
            attempt_no += 1
            trial = 0
            gauss_bins = bin_origin + bin_adjust[attempt_no]

    # only warn about clustering changes if specific parameters were input
    if bin_origin != 180 or smooth_origin is not None:
        if attempt_no > 0.1 * bin_origin:
            if write_name is None:
                warnings.warn('Altered gauss_bins by >10% for clustering.\nYou might want to check cluster plot.')
            else:
                _warn_string = 'Altered gauss_bins by >10% for clustering of ' + write_name + '.\n'
                _warn_string += 'You might want to check cluster plot.'
                warnings.warn(_warn_string)

    return gaussians, Gauss_xvals


def get_intersects(gaussians, distribution, Gauss_xvals, write_plots=None, write_name=None):
    """
    Obtain the intersects of a mixture of Gaussians which have been obtained
    from decomposing a distribution into Gaussians. Additional state limits are
    added at the beginning and end of the distribution.

    Parameters
    ----------
    gaussians : list of lists
        A list of X gaussians.
    distribution : list
        The distribution that Gaussians have been obtained from.
    xline : list
        The x-axis linespace that the distribution spans.
    write_plots : bool, optional
        If true, visualise the states over the raw distribution. The default is None.
    write_name : str, optional
        Filename for write_plots. The default is None.


    Returns
    -------
    all_intersects : list
        All the Gaussian intersects.

    """
    # adding the minimum angle value as the first boundary
    all_intersects = [min(distribution)]
    mean_gauss_xval = []
    for gauss_num in range(len(gaussians)):
        mean_gauss_xval.append(Gauss_xvals[list(gaussians[gauss_num]).index(max(gaussians[gauss_num]))])

    # sort gaussians in order of their mean xval
    reorder_gaussians = [gaussians[mean_gauss_xval.index(mean)] for mean in sorted(mean_gauss_xval)]

    for gauss_index in range(len(reorder_gaussians) - 1):
        # Find indices between neighbouring gaussians
        idx_sign = np.sign(reorder_gaussians[gauss_index] - reorder_gaussians[gauss_index + 1])
        idx = np.argwhere(np.diff(idx_sign)).flatten()
        if len(idx) == 1:
            all_intersects.append(float(Gauss_xvals[idx][0]))
        elif len(idx) != 0:
            # Select the intersect with the maximum probability
            intersect_ymax = max([reorder_gaussians[gauss_index][intersect] for intersect in idx])
            intersect_ymax_index = [item for item in idx if reorder_gaussians[gauss_index][item] == intersect_ymax]
            all_intersects.append(float(Gauss_xvals[intersect_ymax_index]))
        # For gaussian neighbours that don't intersect, set state limit as center between maxima
        elif len(idx) == 0:
            gauss_max1 = list(reorder_gaussians[gauss_index]).index(max(reorder_gaussians[gauss_index]))
            gauss_max2 = list(reorder_gaussians[gauss_index + 1]).index(max(reorder_gaussians[gauss_index + 1]))
            intersect = 0.5 * np.abs(Gauss_xvals[gauss_max2] + Gauss_xvals[gauss_max1])
            all_intersects.append(float(intersect))

    all_intersects.append(max(distribution))

    if write_plots is True:
        if not os.path.exists('ssi_plots/'):
            os.makedirs('ssi_plots/')
        plt.figure()
        plt.ion()
        plt.hist(distribution, bins=360, density=True, alpha=0.5)
        for gauss_index in range(len(reorder_gaussians)):
            plt.plot(Gauss_xvals, reorder_gaussians[gauss_index], lw=2)
        for intersect_index in range(len(all_intersects)):
            plt.axvline(all_intersects[intersect_index], color='k', lw=1, ls='--')
        plt.xlabel('Radians')
        plt.ylabel('Count')
        plt.title(write_name)
        plt.ioff()
        plt.savefig('ssi_plots/' + write_name + ".png")
        plt.close()

    return all_intersects


def determine_state_limits(distr, traj1_len, gauss_bins=180, gauss_smooth=None, write_plots=None, write_name=None):
    """
    Cluster a distribution into discrete states with well-defined limits.
    The function handles both residue angle distributions and water
    distributions. For waters, the assignment of an additional non-angular
    state is performed if changes in pocket occupancy occur. The clustering
    requires that the distribution can be decomposed to a mixture of Gaussians.

    Parameters
    ----------
    distr : list
        Distribution for specific feature.
    gauss_bins : int, optional
        Number of histogram bins to assign for the clustering algorithm.
        The default is 180.
    gauss_smooth : int, optional
        Number of bins to perform smoothing over. The default is ~10% of gauss_bins.
    write_plots : bool, optional
        If true, visualise the states over the raw distribution. The default is None.
    write_name : str, optional
        Filename for write_plots. The default is None.

    Returns
    -------
    list
        State intersects for each cluster in numerical order.

    """
    new_dist = distr.copy()
    distribution = [item for item in new_dist if item != 10000.0]
    # obtaining the gaussian fit
    gaussians, Gauss_xvals = smart_gauss_fit(distribution, traj1_len, gauss_bins, gauss_smooth, write_name)
    # discretising each state by gaussian intersects
    intersection_of_states = get_intersects(gaussians, distribution, Gauss_xvals, write_plots, write_name)
    if distr.count(10000.0) >= 1:
        intersection_of_states.append(20000.0)

    order_intersect = np.sort(intersection_of_states)
    return list(order_intersect)


# -- Functions to operate on discrete states --


def _check(value, x, y):
    """
    Check if a value is between x and y

    Parameters
    ----------
    value : float
        Value of interest.
    x : float
        Limit x.
    y : float
        Limit y.

    Returns
    -------
    int
        Numerical bool if value is between limits x and y.

    """
    if x <= value <= y:
        return 1
    else:
        return 0


def _create_states(data):
    """
    Create states as the partitions between all values in the data.

    Parameters
    ----------
    data : List
        input data.

    Returns
    -------
    partitions : list
        values that partition all the data.

    """
    # Removing all duplicate resid's from the data and sorting numerically
    no_dups = sorted(list(dict.fromkeys(data)))
    # Creating partitions between all the data
    partitions = [num - 0.5 for num in no_dups]
    # Adding the final limit
    partitions.append(no_dups[-1] + 0.5)

    return partitions


def calculate_entropy(state_limits, distribution_list):
    """
    Calculate the Shannon entropy of a distribution as the summation of all
    -p*log(p) where p refers to the probability of a conformational state.

    Parameters
    ----------
    state_limits : list of lists
        A list of values that represent the limits of each state for each
        distribution.
    distribution_list : list of lists
        A list containing multivariate distributions (lists) for a particular
        residue or water

    Returns
    -------
    entropy : float
        The Shannon entropy value

    """

    state_lims = state_limits.copy()
    dist_list = distribution_list.copy()
    # Ignore singular states and corresponding distributions
    state_no = 0
    while state_no < len(state_lims):

        if len(state_lims[state_no]) == 2:
            del dist_list[state_no]
            del state_lims[state_no]

        else:
            state_no += 1

    entropy = 0.0
    if len(state_lims) != 0:
        # subtract 1 since number of states = number of partitions - 1
        mut_prob = np.zeros(([len(state_lims[i]) - 1 for i in range(len(state_lims))]))
        # iterating over every multidimensional index in the array
        it = np.nditer(mut_prob, flags=['multi_index'])

        while not it.finished:
            arrayindices = list(it.multi_index)
            limit_occupancy_checks = np.zeros((len(arrayindices), len(dist_list[0])))

            for dist_num in range(len(arrayindices)):
                limits = [state_lims[dist_num][arrayindices[dist_num]],
                          state_lims[dist_num][arrayindices[dist_num] + 1]]
                distribution = dist_list[dist_num]

                for frame_num in range(len(distribution)):
                    limit_occupancy_checks[dist_num][frame_num] = _check(distribution[frame_num], limits[0], limits[1])
            mut_prob[it.multi_index] = sum(np.prod(limit_occupancy_checks, axis=0)) / len(limit_occupancy_checks[0])
            # calculating the entropy as the summation of all -p*log(p)

            if mut_prob[it.multi_index] != 0:
                entropy += -1 * mut_prob[it.multi_index] * math.log(mut_prob[it.multi_index], 2)
            it.iternext()
    return entropy


def _lim_occ_par(idx, params):
    """
    Calculate the entropy of each state for a subset of the states.

    Parameters
    ----------
    idx : list
        Start and stop indices to define subset of states for calculations.
    params : list of lists
        List of state limits and feature multivariate timeseries distribution.

    Returns
    -------
    entropy : float
        Entropy of each state for a subset of the states.

    """

    state_lims, dist_list = params[0], params[1]

    # Initialize entropy value
    entropy = 0

    # Initialize array for multidimensional discrete state phase space
    mut_prob = np.zeros(([len(state_lims[i]) - 1 for i in range(len(state_lims))]))
    # Extract sizes of each dimension in the mut_prob
    dimension_lists = [list(range(mut_prob.shape[i])) for i in range(len(dist_list))]

    # Obtain indices to iterate over multivariate array
    iterprod = itertools.product(*dimension_lists)
    multiidx_loopno = list(iterprod)

    # Iterate over subset of multivariate array for entropy calculation
    for loopno in multiidx_loopno[idx[0]:idx[1]]:
        arrayindices = list(loopno)
        limit_occupancy_checks = np.zeros((len(arrayindices), len(dist_list[0])))

        for dist_num in range(len(arrayindices)):
            limits = [state_lims[dist_num][arrayindices[dist_num]], state_lims[dist_num][arrayindices[dist_num] + 1]]
            distribution = dist_list[dist_num]

            for frame_num in range(len(distribution)):
                limit_occupancy_checks[dist_num][frame_num] = _check(distribution[frame_num], limits[0], limits[1])

        mut_prob[loopno] = sum(np.prod(limit_occupancy_checks, axis=0)) / len(limit_occupancy_checks[0])
        # calculating the entropy as the summation of all -p*log(p)

        if mut_prob[loopno] != 0:
            entropy += -1 * mut_prob[loopno] * math.log(mut_prob[loopno], 2)
    return entropy


def _divisorGenerator(n):
    """
    Find largest whole number divisors.

    Parameters
    ----------
    n : int
        Value to find whole number divisors of.

    Yields
    ------
    generator object
        All whole number divisors of the number n.

    """
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i * i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield divisor


def calculate_entropy_multthread(state_limits, distribution_list, max_thread_no):
    """
    Calculate the Shannon entropy of a distribution as the summation of all
    -p*log(p) where p refers to the probability of a conformational state.

    Parameters
    ----------
    state_limits : list of lists
        A list of values that represent the limits of each state for each
        distribution.
    distribution_list : list of lists
        A list containing multivariate distributions (lists) for a particular
        residue or water
    max_thread_no : int
        Maximum number of threads to use in the multi-threading.

    Returns
    -------
    entropy : float
        The Shannon entropy value

    """

    state_lims = state_limits.copy()
    dist_list = distribution_list.copy()

    # Ignore singular states and corresponding distributions
    state_no = 0
    while state_no < len(state_lims):

        if len(state_lims[state_no]) == 2:
            del dist_list[state_no]
            del state_lims[state_no]

        else:
            state_no += 1

    entropy = 0
    if len(state_lims) != 0:
        # Initialize array for multidimensional discrete state phase space
        mut_prob = np.zeros(([len(state_lims[i]) - 1 for i in range(len(state_lims))]))
        # Extract sizes of each dimension in the mut_prob
        dimension_lists = [list(range(mut_prob.shape[i])) for i in range(len(dist_list))]
        # Obtain indices to iterate over multivariate array
        iterprod = itertools.product(*dimension_lists)
        # Length of iterations for full array
        multiidx_loopno = len(list(iterprod))
        # Largest possible multi-threading option for array
        threadno = [num for num in list(_divisorGenerator(multiidx_loopno)) if num < max_thread_no + 1]
        multthr = threadno[-1]
        # Start and stop indices for state subsets
        poolprocs1 = list(range(0, multiidx_loopno + 1, int(multthr)))[:-1]
        poolprocs2 = list(range(0, multiidx_loopno + 1, int(multthr)))[1:]
        poolproc = [[i, j] for i, j in zip(poolprocs1, poolprocs2)]

        param = [state_lims, dist_list]

        # Multi-threading entropy calculations
        with Pool() as pool:
            all_entropy = pool.map(partial(_lim_occ_par, params=param), poolproc)

        # Total entropy is sum of all subset entropies
        entropy += sum(all_entropy)

    return entropy


def get_discrete_states(all_data_a, all_data_b, discretize='gaussian', pbc=True, h2o=False, write_plots=False):
    """
    Obtain list of state limits for each feature.

    Parameters
    ----------
    all_data_a : float array
        Trajectory data from the first ensemble.
    all_data_b : float array
        Trajectory data from the second ensemble.
    discretize : str, optional
        Method for state discretization. Options are 'gaussian', which defines
        state limits by gaussian intersects, and 'partition_values', which defines
        state limits by partitioning all values in the data. The default is 'gaussian'.
    pbc : bool, optional
        If true, the apply periodic bounary corrections on angular distribution inputs.
        The input for periodic correction must be radians. The default is True.
    h2o : bool, optional
        If true, the apply periodic bounary corrections for spherical angles
        with different periodicities. The default is False.
    write_plots : bool, optional
        If true, visualise the states over the raw distribution. The default is False.

    Returns
    -------
    ssi_states : list of list
        List of state limits for each feature.

    """

    # Initialize states list
    ssi_states = []

    # Loop over all features
    for residue in range(len(all_data_a)):
        data_a = all_data_a[residue]
        data_b = all_data_b[residue]

        combined_dist = []

        for dist_no in range(len(data_a)):
            # combine the ensembles into one distribution (condition_a + condition_b)
            data_both = list(data_a[dist_no]) + list(data_b[dist_no])
            combined_dist.append(data_both)

        if pbc:
            if h2o:
                combined_dist = correct_spher_angle_periodicity(combined_dist)
            else:
                # Correct the periodicity of angles (in radians)
                combined_dist = [correct_angle_periodicity(distr) for distr in combined_dist]

        if discretize == 'partition_values':
            # Define states as partition between data values
            feat_states = []
            for dim_num in range(len(combined_dist)):
                feat_states.append(_create_states(combined_dist[dim_num]))

        elif discretize == 'gaussian':
            # Saving distribution length
            traj1_len = len([i for i in data_a[0] if i != 10000.0])
            feat_states = []
            for dim_num in range(len(combined_dist)):
                if write_plots:
                    plot_name = "Residue " + str(residue) + ", Dim. " + str(dim_num)
                else:
                    plot_name = None
                try:
                    feat_states.append(
                        determine_state_limits(
                            combined_dist[dim_num], traj1_len,
                            write_plots=write_plots, write_name=plot_name
                        )
                    )
                except Exception:
                    warnings.warn('Distribution ', residue, ' not clustering properly.')

        ssi_states.append(feat_states)

    return ssi_states
