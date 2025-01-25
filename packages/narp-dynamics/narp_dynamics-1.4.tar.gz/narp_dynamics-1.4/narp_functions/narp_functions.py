from .pulses import vector_time_field, set_limits, frequency_field
from .integrator import density_matrix_integrator, hamiltonian
import jax.numpy as jnp
from tqdm import tqdm
from typing import Tuple
from cmap import Colormap
import matplotlib.pyplot as plt

def narp_pulse(
    pulse_center_frequency: float,
    pulse_bandwidth: float,
    pulse_area: float,
    chirp_rate: float,
    notch_type: float,
    notch_bandwidth: float
) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """
    Creation and evaluation of a NARP pulse in the frequency and time domains.

    Args:
        pulse_center_frequency (float): Center frequency of the pulse [PHz].
        pulse_bandwidth (float): FWHM of the power profile of the pulse in frequency [PHZ].
        pulse_area (float): Area of the pulse.
        chirp_rate (float): Chirp rate [fs]^2.
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        notch_bandwidth (float):  FWHM of the power profile of the notch in frequency [PHZ]
    Returns:
        Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]: 
            frequency: Frequency array.
            evaluated: Evaluated field in frequency array.
            time: Time array
            evaluated time field: Evaluated field in time array.

    """
    f_field = lambda f: frequency_field(
        f = f,
        f_0 = pulse_center_frequency,
        pulse_fwhm = pulse_bandwidth,
        pulse_area = pulse_area,
        chirp_rate = chirp_rate,
        notch_type = notch_type,
        notch_fwhm = notch_bandwidth
    )

    max_f = 0.2*pulse_center_frequency
    frequency = jnp.linspace(pulse_center_frequency-max_f, pulse_center_frequency+max_f, 15_000)
    evaluated_f_field = f_field(frequency)

    t_field= lambda t: vector_time_field(
        frequency,
        pulse_center_frequency,
        t,
        pulse_bandwidth,
        pulse_area,
        chirp_rate,
        notch_type,
        notch_bandwidth
    )

    max_t = set_limits(center = 0.0, func = t_field, epsilon = 1e-5, step = 25)
    time = jnp.linspace(-max_t, max_t, 7_500)
    evaluated_t_field = t_field(time)

    return frequency, evaluated_f_field, time, evaluated_t_field

def narp_pulse_dynamics(
    narp_pulse : Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray],
    two_level_resonance_frequency : float
):
    """
    Integrates the Liouville von-Neumann equation for the two-level system interacting
    with the NARP pulse. Returns the density matrix evaluated in each time

    Args:
        narp_pulse (Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]): 
            frequency: Frequency array.
            evaluated: Evaluated field in frequency array.
            time: Time array
            evaluated time field: Evaluated field in time array.

    Return
        jnp.ndarray: Integrated density matrix for each time.
    """
    h = hamiltonian(
        integration_time = narp_pulse[2],
        evaluated_time_field = narp_pulse[3],
        resonance_frequency = two_level_resonance_frequency
    )
    rho = density_matrix_integrator(
        integration_time = narp_pulse[2], 
        H_precomputed = h
    )
    return rho

def area_versus_chirp(
    pulse_center_frequency: float,
    pulse_bandwidth: float,
    notch_type: float,
    notch_bandwidth: float,
    resolution: int
):
    """
    Gives the occupation after the interaction of the pulse with the two-level system
    in terms of variations in area and chirp.

    Args:
        pulse_center_frequency (float): Center frequency of the pulse [PHz].
        pulse_bandwidth (float): FWHM of the power profile of the pulse in frequency [PHZ].
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        notch_bandwidth (float):  FWHM of the power profile of the notch in frequency [PHZ].
        resolution (int): Resolution of the grid of parameters.
    """
    max_chirp = 5*(0.44/pulse_bandwidth)**2
    pulse_areas = jnp.linspace(0.01*jnp.pi, 10*jnp.pi, resolution)
    chirp_rates = jnp.linspace(-max_chirp, max_chirp, resolution)
    pulse_areas_grid, chirp_rates_grid = jnp.meshgrid(pulse_areas, chirp_rates)
    params = {
        "pulse_center_frequency": pulse_center_frequency,
        "pulse_bandwidth": pulse_bandwidth,
        "notch_bandwidth": notch_bandwidth,
        "notch_type": notch_type
    }
    occupations = []
    pulse_areas_flat = pulse_areas_grid.flatten()
    chirp_rates_flat = chirp_rates_grid.flatten()
    total_iterations = len(pulse_areas_flat)
    for pulse_area, chirp_rate in tqdm(zip(pulse_areas_flat, chirp_rates_flat),
            total=total_iterations, desc="Computing occupations"):
        params["chirp_rate"] = chirp_rate
        params["pulse_area"] = pulse_area
        pulse = narp_pulse(**params)
        occupation = narp_pulse_dynamics(pulse, params["pulse_center_frequency"])[-1, 1, 1]
        occupations.append(jnp.real(occupation))
    return pulse_areas_grid, chirp_rates_grid, jnp.array(occupations).reshape(chirp_rates_grid.shape)

def notch_versus_chirp(
    pulse_center_frequency,
    pulse_bandwidth,
    notch_type,
    pulse_area,
    resolution
): 
    """
    Gives the occupation after the interaction of the pulse with the two-level system
    in terms of variations in notch width and chirp.

    Args:
        pulse_center_frequency (float): Center frequency of the pulse [PHz].
        pulse_bandwidth (float): FWHM of the power profile of the pulse in frequency [PHZ].
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        pulse_area (float): Area of the pulse.
        resolution (int): Resolution of the grid of parameters.
    """
    max_chirp = 5*(0.44/pulse_bandwidth)**2
    notch_widths = jnp.linspace(pulse_bandwidth/6, pulse_bandwidth, resolution)
    chirp_rates = jnp.linspace(-max_chirp, max_chirp, resolution)
    notch_widths_grid, chirp_rates_grid = jnp.meshgrid(notch_widths, chirp_rates)
    params = {
        "pulse_center_frequency": pulse_center_frequency,
        "pulse_bandwidth": pulse_bandwidth,
        "pulse_area": pulse_area,
        "notch_type": notch_type
    }
    occupations = []
    notch_widths_flat = notch_widths_grid.flatten()
    chirp_rates_flat = chirp_rates_grid.flatten()
    total_iterations = len(notch_widths_flat)
    for notch_width, chirp_rate in tqdm(
        zip(notch_widths_flat, chirp_rates_flat),
        total=total_iterations,
        desc="Computing occupations"
    ):
        params["notch_bandwidth"] = notch_width
        params["chirp_rate"] = chirp_rate
        pulse = narp_pulse(**params)
        occupation = narp_pulse_dynamics(pulse, params["pulse_center_frequency"])[-1, 1, 1]
        occupations.append(jnp.real(occupation))
    return notch_widths_grid, chirp_rates_grid, jnp.array(occupations).reshape( chirp_rates_grid.shape)

def notch_versus_area(
    pulse_center_frequency,
    pulse_bandwidth,
    chirp_rate,
    notch_type,
    resolution
): 
    """
    Gives the occupation after the interaction of the pulse with the two-level system
    in terms of variations in notch width and chirp.

    Args:
        pulse_center_frequency (float): Center frequency of the pulse [PHz].
        pulse_bandwidth (float): FWHM of the power profile of the pulse in frequency [PHZ].
        notch_type (float): [0,1,2,3] -> gaussian, sech^2, lorentzian, psquare.
        pulse_area (float): Area of the pulse.
        resolution (int): Resolution of the grid of parameters.
    """
    notch_widths = jnp.linspace(pulse_bandwidth/6, pulse_bandwidth, resolution)
    pulse_areas = jnp.linspace(0.01*jnp.pi, 10*jnp.pi, resolution)
    notch_widths_grid, pulse_areas_grid = jnp.meshgrid(notch_widths, pulse_areas)
    params = {
        "pulse_center_frequency": pulse_center_frequency,
        "pulse_bandwidth": pulse_bandwidth,
        "chirp_rate": chirp_rate,
        "notch_type": notch_type
    }
    occupations = []
    notch_widths_flat = notch_widths_grid.flatten()
    pulse_areas_flat = pulse_areas_grid.flatten()
    total_iterations = len(notch_widths_flat)
    for notch_width, pulse_area in tqdm(
        zip(notch_widths_flat, pulse_areas_flat),
        total=total_iterations,
        desc="Computing occupations"
    ):
        params["notch_bandwidth"] = notch_width
        params["pulse_area"] = pulse_area
        pulse = narp_pulse(**params)
        occupation = narp_pulse_dynamics(pulse, params["pulse_center_frequency"])[-1, 1, 1]
        occupations.append(jnp.real(occupation))
    return notch_widths_grid, pulse_areas_grid, jnp.array(occupations).reshape(pulse_areas_grid.shape)

tex_fonts = {
    # Use LaTeX to write all text
    "text.usetex": True,
    "font.family": "serif",
    # Use 10pt font in plots, to match 10pt font in document
    "axes.labelsize": 8,
    "font.size": 8,
    # Make the legend/label fonts a little smaller
    "legend.fontsize": 7,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8
}

cmap = Colormap('cmasher:sapphire').to_mpl()
plt.style.use('seaborn-v0_8-white')
plt.rcParams.update(tex_fonts)

def plot_fields(
    narp_pulse : Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray],
    t_color : str = 'black',
    f_color : str = 'black'
):
    """
    Plots the evaluated time and frequency fields.

    Args:
        narp_pulse (Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]): 
            frequency: Frequency array.
            evaluated: Evaluated field in frequency array.
            time: Time array
            evaluated time field: Evaluated field in time array.
        t_color (str): Color of the time plot. 
        f_color (str): Color of the frequency plot.
    """
    fig, axs = plt.subplots(2, 1, figsize = (3.4, 4.0))
    plt.subplots_adjust(hspace = 0.6)
    
    axs[0].plot(narp_pulse[2], jnp.abs(narp_pulse[3]),
        linewidth = 2, color = t_color)
    axs[0].set_xlabel(r'$t$  [fs]')
    axs[0].set_ylabel(r'$|E(t)|$  \ [V/m]')
    axs[0].tick_params(axis  = 'both', which = 'both',
        direction = 'out', length = 3.5, width = 1)
    axs[0].set_title('Time Field')

    axs[1].plot(narp_pulse[0], jnp.abs(narp_pulse[1]),
        linewidth = 2, color = f_color)
    current_xticks = axs[1].get_xticks()
    axs[1].set_xlim(jnp.min(narp_pulse[0]), jnp.max(narp_pulse[0]))
    new_xticklabels = [int(tick*1000) for tick in current_xticks]
    axs[1].set_xticks(current_xticks)
    axs[1].set_xticklabels(new_xticklabels)
    axs[1].set_xlabel(r'$f$ [THz]')
    axs[1].set_ylabel(r'$|E(f)| \ \ [V/m]$')
    axs[1].tick_params(axis  = 'both', which = 'both',
        direction = 'out', length = 3.5, width = 1)
    axs[1].set_title('Frequency Field')
    plt.show()

def plot_occupations(
    narp_pulse : Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray],
    rho : jnp.ndarray,
    g_color : str = 'black',
    e_color : str = 'black'
):
    """
    Plots the evaluated occupations of the two-level system interacting with the pulse.

    Args:
        narp_pulse (Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]): 
            frequency: Frequency array.
            evaluated: Evaluated field in frequency array.
            time: Time array
            evaluated time field: Evaluated field in time array.
        rho (jnp.ndarray): Integrated density matrix for each time.
        g_color (str): Color of the ground state population. 
        e_color (str): Color of the excited state population.
    """
    fig, axs = plt.subplots(2, 1, figsize = (3.4, 4.0))
    plt.subplots_adjust(hspace = 0.6)

    axs[0].plot(narp_pulse[2], jnp.real(rho[:, 0, 0]),
        linewidth = 2, color = g_color)
    axs[0].set_xlabel(r'$t$  [fs]')
    axs[0].set_ylabel(r'$\rho_{00} \ (|g\rangle)$')
    axs[0].set_title('Ground State Population')

    axs[1].plot(narp_pulse[2], jnp.real(rho[:, 1, 1]),
        linewidth = 2, color = e_color)
    axs[1].set_xlabel(r'$t$  [fs]')
    axs[1].set_ylabel(r'$\rho_{11} \ (|e\rangle)$')
    axs[1].set_title('Excited State Population')

def plot_surfaces(
    grid_1,
    grid_2,
    occupations
):
    fig, axs = plt.subplots(1, figsize = (3.8, 3.2))
    levels = jnp.linspace(jnp.min(occupations), jnp.max(occupations), num = 10)
    plt.contourf(grid_1, grid_2, occupations, levels = levels, cmap = cmap)
    cbar = plt.colorbar()
    current_ticks = cbar.get_ticks()
    formatted_tick_labels = [f"{tick:.1f}" for tick in current_ticks]
    cbar.set_ticks(current_ticks)  
    cbar.set_ticklabels(formatted_tick_labels) 
    plt.show()