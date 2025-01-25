```python
from narp_functions import narp_pulse, narp_pulse_dynamics
from narp_plotting_functions import plot_fields, plot_occupations
import jax.numpy as jnp
```

# Basic Usage


```python
pulse = narp_pulse(
    pulse_center_frequency = 0.322, #[PHz]
    pulse_bandwidth = 0.022, #[PHz] (20 fs pulse)
    pulse_area = 6*jnp.pi,
    chirp_rate = 900, #[ps]^2
    notch_type = 0,
    notch_bandwidth = 0.022/5 #[PHz]
)
plot_fields(pulse)
```


    
![png](README_files/README_2_0.png)
    



```python
rho = narp_pulse_dynamics(pulse, 0.322) # (Resonance)
plot_occupations(pulse, rho)
```


    
![png](README_files/README_3_0.png)
    


# Parameter Space

## Area versus Chirp


```python
from narp_functions import area_versus_chirp, notch_versus_chirp, notch_versus_area
from narp_plotting_functions import plot_surfaces
```


```python
pulse_areas_grid, chirp_rates_grid, occupations_matrix = area_versus_chirp(
    pulse_center_frequency = 0.322, #[PHz]
    pulse_bandwidth = 0.022, #[PHz] (20 fs pulse)
    notch_type = 0,
    notch_bandwidth = 0.022/5, #[PHz]
    resolution = 25
)
plot_surfaces(chirp_rates_grid, pulse_areas_grid, occupations_matrix)
```

    Computing occupations: 100%|██████████| 625/625 [03:00<00:00,  3.47it/s]



    
![png](README_files/README_7_1.png)
    


# Notch versus Chirp


```python
pulse_areas_grid, notch_widths_grid, occupations_matrix = notch_versus_chirp(
    pulse_center_frequency = 0.322, #[PHz]
    pulse_bandwidth = 0.022, #[PHz] (20 fs pulse)
    notch_type = 0,
    pulse_area = 8*jnp.pi,
    resolution = 25
)
plot_surfaces(notch_widths_grid, pulse_areas_grid, occupations_matrix)
```

    Computing occupations: 100%|██████████| 625/625 [02:58<00:00,  3.50it/s]



    
![png](README_files/README_9_1.png)
    


# Notch versus Area


```python
pulse_areas_grid, notch_widths_grid, occupations_matrix = notch_versus_area(
    pulse_center_frequency = 0.322, #[PHz]
    pulse_bandwidth = 0.022, #[PHz] (20 fs pulse)
    chirp_rate = 600,
    notch_type = 0,
    resolution = 25
)
plot_surfaces(notch_widths_grid, pulse_areas_grid, occupations_matrix)
```

    Computing occupations: 100%|██████████| 625/625 [02:55<00:00,  3.56it/s]



    
![png](README_files/README_11_1.png)
    

