

== Digitization Simulation ==


The mean number of ionization electrons $`\bar{N_e}`$ produced in each hit is proportional to the energy deposition $\Delta E$, namely:

```math
\bar{N_e} = \frac{\Delta E}{W_i}
```

Where $W_i$ is the ionization potential of the gas ($W_i = 46-2$ eV/pair for He/CF4 60/40)\\
Thus, the actual number of ionization electrons ${N_e}$ is obtained  from a Poisson distribution with a mean of $\bar{N_e}$.
The ionization electrons will diffuse in the drift region, thus/hence the coordinate $x_{hit}$ and $y_{hit}$ of each hit (and of the ionization electrons) is modified applying Gaussian fluctuations with variance: [https://arxiv.org/pdf/2007.00608.pdf]:
$$ \sigma_D^2  = D_T^2 \cdot z$$
Where $D_T^2$ is the transverse diffusion coefficients, and $z$ is the distance of the hit from the first GEM.\\
When the ionization electrons arrive at the 3-GEM stack, only fluctuations of the gain of the first GEM are relevant, while the gain of the following two GEMs can be assumed constant. Hence, the secondary electrons produced by the first GEM are obtained from the sum of $N_e$ exponential distributions $N_e^{G_1, k}$ with mean $G_{GEM}$ (gain of the a GEM foil).
$$ N_e^{G1, tot} = \sum_{k}^{N_e} N_e^{G_1, k} $$
Then the secondary electrons go throughout the second and the third GEM foil that are assumed to have a constant gain $G_{GEM}$. So the total number of multiplication electrons after the third GEM foil is:
$$ N_e^{tot} = N_e^{G1, tot} \cdot (G_{GEM})^2$$
Since CYGNO has an optical readout, the number of photons produces in the multiplication process is the relevant physical quantity that must be computed. To do so, a conversion factor of 0.07 $\gamma$/e is used [quote]. We are currently working on a simulation that does not use such a parameter. The mean value of photons produced is:
$$ \bar{N_{\gamma}}^{tot} = N_e^{tot} \cdot  0.07 \; \gamma /e$$
The production of photons is obtained from a Poisson distribution with mean value $\bar{N_{\gamma}}^{tot}$\\
The number of photons hitting the sensor  depends on the solid angle ratio $\Omega$, namely:
$$  N_{\gamma} = N_{\gamma}^{tot} \cdot \Omega $$Where the solid angle radio is [quote]:
$$\Omega =\frac{1}{\left(4\left(\delta+1\right)a\right)^2}$$ 
Where (for LIME or LEMON)
$$  \delta = \frac{d_{obj}}{d_{img}} $$
Where $d_{obj}$ and $d_{img}$ are respectively the dimensions of the "object"? and the image.
And $a$ is the aperture of the camera (?).\\
During the electron-multiplication process, multiplication electrons (as well as photons) undergo further diffusion in the GEM structure. So the coordinates $x$, $y$ of the ionization electrons are further modified applying Gaussian fluctuations with variance $\sigma_{T_0}$ [quote].
Applying both the diffusion correction due to drift and to the multiplication process, we can apply a single Gaussian fluctuation to the hit coordinates $x_hit$ and $y_hit$, with a variance:
$$ \sigma_T^2 = \sigma_{T_0}^2+ \sigma_D^2 $$
So for each hit a number $N_{\gamma}$ of position from  a 2D Gaussian distribution around the initial hit position and  with variance $\sigma_T^2$
The parameters used for the simulation are shown in Table \ref{table:first_set_LEMON_LIME_pars} and \ref{table:second_set_LEMON_LIME_pars}, for LIME and LEMON.


|       | $`W_i`$ (eV /pair) | $`G_{GEM}`$ | $`\gamma/e`$ | $`\Omega`$ | $`a`$ | $`\delta`$ | obj_dim (cm) | image_dm (cm) |
|-------|--------------------|-------------|--------------|------------|-------|------------|--------------|---------------|
| LEMON | 46.2               | 123         | 0.7          |            | 0.95  |            | 25           | 1.33          |
| LIME  | 46.2               | 123         | 0.7          |            | 0.95  |            | 35           | 1.33          |


    \includegraphics[scale=0.5]{immagini/digitization_schema_hit_petrucci.png}



== Saturation Effect ==
