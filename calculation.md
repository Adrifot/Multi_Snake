# Tuning configuration variables
## Energy Economics
### Calculations
Let's review the following variables needed in the energy economics of this simulation.
 I will be considering the most common gene expression values (bit encodings $0b01$ and $0b10$):
- $E_{max} - \text{maximum snake energy}$
- $TC_{avg} - \text{average terrain cost of a map}$
- $F_E - \text{energy gained on consuming food}$
- $X - \text{energy shrinking interval}$
- $W - \text{map width and height}$
- $F_{nr} - \text{maximum food count present at the same time}$ 
- $S_{nr} - \text{maximum snake count present at the same time}$

I ran 1,000 Perlin noise-generated maps of size 50x50 and computed the overall average terrain cost $TC_{avg} = 2.8$

For the final simulation, the map size is 100x100 tiles ($W = 100$).

Knowing $W$, we can calculate the total map area: $A_{map} = 10,000 \text{ tiles}$.

In order to find an adequate value for $E_{max}$, I decided that a snake should be able to cross about $5$% of the map area before shrinking:

\[
\begin{aligned}
\frac{E_{max}}{TC_{avg}} &= 0.05 \times A_{map} \\
E_{max} &= 0.05 \times A_{map} \times TC_{avg} \\
E_{max} &= 0.05 \times (100 \times 100) \times 2.8 \\
E_{max} &= 1,400.
\end{aligned}
\]

Now that we have a value for $E_{max}$ we can calculate $X$:
- $l_0 = l_{min} = 3  \text{ (initial snake length)}$
- $D = 50 \text{ (number of tiles a snake can travel without food before shrinking)}$

Then:
\[
\begin{aligned}
X &= D \times TC_{avg} \\
X &= 50 \times 1.6 \\
X &= 80.
\end{aligned}
\]

Food should replenish lost energy and give a surplus, thus: $F_E = 1.25X = 100$

$V = 10$ (vision range), so each snakes has a visibility area of around $(2V+1)^2 \approx 440$ tiles. We want around 1-2 foods in a vision window - 2 foods per 450 tiles:
\[
F_{nr} = \frac{A_{map}}{450/2} \approx \frac{10,000}{225} \approx 44.
\]

In order to choose an adequate $S_{nr}$, we need to consider the value of $F_{nr}$ and how much competition we want in the simulation. As I don't want snakes to overrun the map, but still want to keep competition, I will set the following ratio:
\[
\frac{S_{nr}}{F_{nr}} = 0.6
\]
Thus: $S_{nr} = 44 \times 0.6 \approx 26 $ snakes.

### Post-testing calibration:
- Too many snakes died of shrinking => incresed $X$ to $200$ and $F_{E}$ to $250$.
- No snakes had any issues with energy => decreased $E_{max}$ to $1000$.
