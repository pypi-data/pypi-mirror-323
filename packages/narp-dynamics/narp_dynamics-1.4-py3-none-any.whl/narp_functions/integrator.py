import jax.numpy as jnp
from jax import jit, vmap, lax
from functools import partial

@partial(jit, static_argnames = ['resonance_frequency'])
def hamiltonian(
    integration_time: jnp.ndarray,
    evaluated_time_field: jnp.ndarray,
    resonance_frequency: float
) -> jnp.ndarray:
    """
    Calculates the Rabi Hamiltonian in the rotation frame under the rotating wave
    approximation.
    
    Args:
        integration_time (jnp.ndarray): Selected time array to perform the integration.
        evaluated_time_field (jnp.ndarray): Evaluated NARP time field in integration_time.
        resonance_frequency(jnp.ndarray): Resonance frequency of the two-level system.

    Returns:
        jnp.ndarray: Evaluated Rabi Hamiltonian.
    """
    unwrapped_phase = jnp.unwrap(-jnp.angle(evaluated_time_field))
    dt = integration_time[1]-integration_time[0]
    phase_rate = jnp.gradient(unwrapped_phase, dt)
    delta = 2*jnp.pi*resonance_frequency - phase_rate
    rabi = jnp.abs(evaluated_time_field)
    H1 = -0.5*delta[:, None, None]*jnp.array([[1, 0], [0, -1]])
    H2 = -0.5*rabi[:, None, None]*jnp.array([[0, 1], [1, 0]])
    return H1 + H2

# Define the commutator function
@jit
def commutator(
    A: jnp.ndarray, 
    B: jnp.ndarray
) -> jnp.ndarray:
    return jnp.dot(A, B) - jnp.dot(B, A)

# Define the derivative function
@jit
def drho_dt(
    rho: jnp.ndarray,
    H: jnp.ndarray
) -> jnp.ndarray:
    return -1j*commutator(H, rho)

# RK4 implementation for the matrix differential equation
@jit
def rk4_step(
    rho: jnp.ndarray,
    H: jnp.ndarray, 
    H_next: jnp.ndarray,
    dt: jnp.ndarray
) -> jnp.ndarray:
    """
    Perform one RK4 step using H for k1, k2, k3 and H_next for k4.
    """
    k1 = drho_dt(rho, H)
    k2 = drho_dt(rho + 0.5 * dt * k1, H)
    k3 = drho_dt(rho + 0.5 * dt * k2, H)
    k4 = drho_dt(rho + dt * k3, H_next)
    return rho + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

@jit
def density_matrix_integrator(
    integration_time: jnp.ndarray,
    H_precomputed: jnp.ndarray
) -> jnp.ndarray:
    """
    Liouville von-Neumann equation integrator for the two-level system interacting
    with the NARP pulse. Returns the density matrix evaluated in each time.

    Args:
        integration_time (jnp.ndarray): Selected time array to perform the integration.
        H_precomputed (jnp.ndarray): Evaluated Hamiltonian in the integration_time.

    Return
        jnp.ndarray: Integrated density matrix for each time.
    """

def density_matrix_integrator(integration_time, H_precomputed):
    rho0 = jnp.array([[1, 0], [0, 0]], dtype=jnp.complex64) 
    dt = jnp.diff(integration_time) 

    def step(carry, inputs):
        rho, _ = carry
        H, H_next, dt_step = inputs
        rho_next = rk4_step(rho, H, H_next, dt_step)
        return (rho_next, None), rho_next

    H_pairs = jnp.stack([H_precomputed[:-1], H_precomputed[1:]], axis=1)
    inputs = (H_pairs[:, 0], H_pairs[:, 1], dt)

    _, rho_values = lax.scan(step, (rho0, None), inputs)
    rho_values = jnp.vstack([rho0[None, :], rho_values])
    
    return rho_values