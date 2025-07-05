import numpy as np

# Parameters (explicitly from Table S1)
beta = 0.5      # Horizontal gene transfer propensity (range: 0.01–1.0)
mu = 1e-3       # Spontaneous module loss rate (range: 10^-4–10^-2)
phi = 1e-2      # Metabolic cost of carrying a module (range: 10^-3–10^-1)

# Time settings
time_steps = np.linspace(0, 200, 1000)
dt = time_steps[1] - time_steps[0]

# Number of lineages
S = 10000

# Initialize lineages explicitly
def initialize_S_lineages(S):
    # Initial random occupancy (small initial values)
    return np.random.rand(S)

# Stochastic simulation explicitly based on pseudocode provided
def run_stochastic_simulation(beta, mu, phi, S, dt, time_steps):
    x = initialize_S_lineages(S)
    M_values = []

    for t in time_steps:
        p_gain = beta * np.mean(x) * (1 - x) * dt
        p_loss = (mu + phi) * x * dt
        
        # Explicit update via Bernoulli trials (probabilistic simulation)
        gain = np.random.binomial(1, np.clip(p_gain, 0, 1))
        loss = np.random.binomial(1, np.clip(p_loss, 0, 1))
        x += gain - loss
        
        # Explicitly ensure occupancy remains between 0 and 1
        x = np.clip(x, 0, 1)
        
        # Explicitly record community mean occupancy
        M_values.append(np.mean(x))

    return M_values

# Run the simulation explicitly
M_values = run_stochastic_simulation(beta, mu, phi, S, dt, time_steps)

# Output explicitly for further analysis
np.savetxt('../results/module_occupancy.txt', np.column_stack((time_steps, M_values)), header="Time\tOccupancy")

