"""Finite-difference solve of the 2D wave equation u_tt = Δu for a ring wave converging on the origin.

Returns the visible window's intensity |u|^2 at every saved step plus the peak (sup) intensity curve.
Cached to build/wave_cache.npz.
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "build/wave_cache.npz"

L = 1.6          # half-width of the simulated domain (visible window is [-1, 1]^2)
N = 640          # grid points per side
R0 = 0.8         # initial ring radius
SIG = 0.035      # ring thickness
T_END = 1.75     # simulated time span


def solve():
    if CACHE.exists():
        d = np.load(CACHE)
        return d["frames"], d["taus"], d["peak"]
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    dt = 0.45 * dx
    X, Y = np.meshgrid(x, x)
    R = np.hypot(X, Y)
    g = np.exp(-((R - R0) / SIG) ** 2)
    gp = -2 * (R - R0) / SIG ** 2 * g          # g'(r - R0)
    u0 = g
    v0 = gp                                     # u = g(r + t) moves inward
    lap = lambda u: (np.roll(u, 1, 0) + np.roll(u, -1, 0) + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4 * u) / dx ** 2
    u_prev = u0
    u = u0 + dt * v0 + 0.5 * dt ** 2 * lap(u0)
    # absorbing-ish sponge near the boundary
    damp = np.clip((R - (L - 0.35)) / 0.35, 0, 1) ** 2 * 0.08
    vis = slice(int((L - 1) / (2 * L) * N), int((L + 1) / (2 * L) * N))
    steps = int(T_END / dt)
    frames, taus, peak = [], [], []
    for k in range(steps):
        if k % 2 == 0:
            w = u[vis, vis]
            I = (w * w).astype(np.float32)
            frames.append(I[::2, ::2].copy() if I.shape[0] > 400 else I.copy())
            taus.append((k + 1) * dt)
            peak.append(float(I.max()))
        u_next = (2 * u - u_prev + dt ** 2 * lap(u)) * (1 - damp)
        u_prev, u = u, u_next
    frames = np.stack(frames)
    taus, peak = np.array(taus), np.array(peak)
    np.savez_compressed(CACHE, frames=frames, taus=taus, peak=peak)
    return frames, taus, peak


if __name__ == "__main__":
    f, t, p = solve()
    i = p.argmax()
    print(f.shape, "focus tau", t[i], "peak/initial", p[i] / p[0], "mean/initial", p.mean() / p[0])
