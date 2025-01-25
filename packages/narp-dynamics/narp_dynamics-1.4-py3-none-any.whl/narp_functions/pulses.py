import jax.numpy as jnp
from jax import vmap, jit
from functools import partial
from collections.abc import Callable

# Definition of Pulse Shapes
@jit
def gaussian(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Gaussian pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return jnp.exp(-0.5*((2*jnp.pi*(f-f_0))/gamma_0)**2)

@jit
def sech2(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Sech^2 pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return 1/jnp.cosh((2*jnp.pi*(f-f_0))/gamma_0)**2

@jit
def lorentzian(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Lorentzian pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile)..

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return 1/(1+((2*jnp.pi*(f-f_0))/gamma_0)**2)

@jit
def psquare(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float,
    smoothness: float = 0.50
) -> jnp.ndarray:
    """
    Smoothed square pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: evaluated electric field in frequency domain.
    """
    left_edge = 1/(1+jnp.exp(-(2*jnp.pi*(f-(f_0-gamma_0)))/(gamma_0*smoothness)))
    right_edge = 1/(1+jnp.exp((2*jnp.pi*(f-(f_0+gamma_0)))/(gamma_0*smoothness)))
    return left_edge*right_edge

# Definition of Chirp Function
@jit
def chirp_function(
    f: jnp.ndarray,
    f_0: float,
    alphap: float
) -> jnp.ndarray:
    """
    Chirp function that produces a linear instantaneous shift in the field frequency.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        alphap (float): Chirp rate [fs]^2.

    Return:
        jnp.ndarray: Evaluated chirp function in the frequency domain.
    """
    return jnp.exp(0.5j*alphap*(2*jnp.pi*(f-f_0))**2)


# Definition of Notches Functions
# all gammas_0 are defined based on the FWHM of the power profile of each pulse

def gaussian_notch(
    f: jnp.ndarray,
    f_0: float,
    notch_fwhm: float
) -> jnp.ndarray:
    """
    Gaussian notch function. 

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated gaussian notch function in the frequency domain.
    """
    gamma_0 = (notch_fwhm*jnp.pi)/jnp.sqrt(jnp.log(2))
    return 1-gaussian(f, f_0, gamma_0)

def sech2_notch(
    f: jnp.ndarray,
    f_0: float,
    notch_fwhm: float
) -> jnp.ndarray:
    """
    Sech^2 notch function. 

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated sech^2 notch function in the frequency domain.
    """
    gamma_0 = (jnp.pi * notch_fwhm)/jnp.arccosh(2**(1/4))
    return 1-sech2(f, f_0, gamma_0)

def lorentzian_notch(
    f: jnp.ndarray,
    f_0: float,
    notch_fwhm: float
) -> jnp.ndarray:
    """
    Lorentzian notch function. 

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated lorentzian notch function in the frequency domain.
    """
    gamma_0 = (jnp.pi*notch_fwhm)/jnp.sqrt(jnp.sqrt(2)-1)
    return 1-lorentzian(f, f_0, gamma_0)

def psquare_notch(
    f: jnp.ndarray,
    f_0: float,
    notch_fwhm: float
) -> jnp.ndarray:
    """
    Lorentzian notch function. 

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated lorentzian notch function in the frequency domain.
    """
    return 1-psquare(f, f_0, notch_fwhm/2)

# Function list for static selection
notch_functions = [
    gaussian_notch,
    sech2_notch,
    lorentzian_notch,
    psquare_notch, 
]

# Construction of the full NARP pulse in frequency domain
def frequency_field(
    f: jnp.ndarray,
    f_0: float,
    pulse_fwhm: float,
    pulse_area: float,
    chirp_rate: float,
    notch_type: int,
    notch_fwhm: float,
) -> jnp.ndarray:
    """
    NARP pulse in the frequency domain.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        pulse_fwhm (float): Pulse bandwidth (power profile) [PHz].
        pulse_area (float): Pulse area.
        chirp_rate (float): Chirp rate [fs]^2.
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated NARP pulse in the frequency domain.
    """
    selected_notch = notch_functions[notch_type]
    gamma_0 = (pulse_fwhm*jnp.pi)/jnp.sqrt(jnp.log(2))
    spectrum = gaussian(f, f_0, gamma_0)
    notch = selected_notch(f, f_0, notch_fwhm)
    chirp = chirp_function(f, f_0, chirp_rate)
    return spectrum*notch*chirp*pulse_area

# Inverse Fourier for time pulse generation

@partial(jit, static_argnames=["notch_type"]) 
def scalar_time_field(
    f: jnp.ndarray,
    f_0: float,
    t: float,
    pulse_fwhm: float,
    pulse_area: float,
    chirp_rate: float,
    notch_type: int,
    notch_fwhm: float,
) -> jnp.ndarray:
    """
    NARP pulse for an scalar time.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        t (float): Point in time to evaluate the field [fs].
        pulse_fwhm (float): Pulse bandwidth (power profile) [PHz].
        pulse_area (float): Pulse area.
        chirp_rate (float): Chirp rate [fs]^2.
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        notch_fwhm (float): Notch bandwidth (power profile) [PHz].

    Return:
        jnp.ndarray: Evaluated NARP pulse in the frequency domain.
    """
    pulse = lambda f: frequency_field(
        f = f,
        f_0 = f_0,
        pulse_fwhm = pulse_fwhm,
        pulse_area = pulse_area,
        chirp_rate = chirp_rate,
        notch_type = notch_type,
        notch_fwhm = notch_fwhm
    )
    df = f[1]-f[0]
    integrand = pulse(f)*jnp.exp(-1j*2*jnp.pi*f*t)
    return jnp.sum(integrand)*df

vector_time_field = vmap(
    scalar_time_field, 
    in_axes=(None, None, 0, None, None, None, None, None)
)

def set_limits(
    func: Callable,
    center: float,
    epsilon: float,
    step: float,
    max_iterations: int = 10_000
) -> float:
    """
    Function to set the correct time limits independent of pulse characteristics.

    Args:
        func (function): Function to evaluate the limits.
        center (float): Center of the interval to search for the limit.
        epsilon (float): Minimum value of the function to set the limit.
        step (float): Size of the steps.
        max_iteration (float): Maximun number of iterations to find the limit.
    Return:
        float: Limit to evaluate the function and obtain the epsilon value.
    """
    x = center  
    for _ in range(max_iterations):
        if abs(func(jnp.array([x]))) <= epsilon:
            return x
        x += step
    return x  