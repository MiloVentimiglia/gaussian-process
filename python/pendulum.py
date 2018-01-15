#!/usr/bin/env python3
# coding=utf-8

import scipy.integrate as integrate
import numpy as np
import matplotlib.pyplot as plt


GRAV = 9.81
LENGTH = 1
MASS = 1
INERTIA = MASS * LENGTH ** 2

# Times are in seconds.
DT = 0.01
T0 = 0
TF = 10

# Initial condition.
X0 = np.array([np.pi / 2, 0])

NOISE_MEAN = 0
NOISE_SIGMA = 0.01
DIST_MEAN = 0
DIST_SIGMA = 1

# Controller gains.
K = np.array([1, 1])

# Operating point.
REF = np.array([np.pi, 0])


def disturbance(mean, sigma):
    ''' Normally distributed disturbance. '''
    return np.random.normal(mean, sigma)


def noise(mean, sigma):
    ''' Normally distributed sensor noise. '''
    return np.random.normal(mean, sigma)


def control(y):
    ''' Control signal. '''
    # Simple PD controller.
    return -np.dot(K, y)


def f(x, t, u):
    ''' State-update function: dx/dt = f(x). '''
    x1dot = x[1]
    x2dot = -GRAV / LENGTH * np.sin(x[0]) + u
    return np.array([x1dot, x2dot])


def out(x):
    ''' Output function: y = g(x) '''
    return x


def step(x, u, dt):
    ''' Simulate the system for a single timestep. '''
    # Model uncertainty.
    d = disturbance(DIST_MEAN, DIST_SIGMA)

    # Integrate the system over a single timestep.
    x = integrate.odeint(f, x, [0, dt], args=(u + d,))
    x = x[1, :]

    # Sensor noise.
    n = noise(NOISE_MEAN, NOISE_SIGMA)

    # System output.
    y = out(x) + n

    return x, y


def main():
    # Initialize the system.
    # Subtract operating point to put us into reference coordinates.
    x = X0 - REF
    y = out(x)
    t = T0
    u = 0

    ts = np.array(t)
    ys = np.array([y])
    us = np.array(u)

    # Simulate the system.
    while t <= TF:
        # Simulate the system for one time step.
        x, y = step(x, u, DT)

        # Calculate control input for next step based on system output.
        u = control(y)

        t = t + DT

        # Record results.
        ts = np.append(ts, t)
        ys = np.append(ys, [y], axis=0)
        us = np.append(us, u)

    # Add operating point back to get back to normal coordinates.
    ys = ys + np.tile(REF, (ys.shape[0], 1))

    # Plot the results.
    plt.plot([T0, TF], [REF[0], REF[0]], label='Reference Angle (rad)')
    plt.plot(ts, ys[:, 0], label='Angle (rad)')
    plt.plot(ts, ys[:, 1], label='Angular Velocity (rad/s)')
    plt.plot(ts, us, label=u'Applied Torque (N·m)')

    plt.xlabel('Time (s)')
    plt.ylabel('Signals')
    plt.title('Inverted Pendulum')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    main()