# Optimisation_Metaheuristique

## Installation
You first require to have python install on your device.

All the libraries necessary are imported at the beginning of the code.
You need to install them with the command pip.

pip install -U matplotlib

To display graphics, you also need to install plotly and Kaleido with :
pip install -U matplotlib
pip install plotly
pip install -U kaleido

## Run the code


The function that runs the code is NSGA_II().

NSGA_II(population_size=200,nb_generations=100, removeParameter=False, show_convergence=False)


As you can see, the arguments will take some values if we don't specify them.
By default, the function try to optimise the 3 criteria : CostEx, Latency and Reliability.
The argument removeParameter allow to remove one of the criteria.

By default, the function displays graphics at dor the first and the last generation.
The argument show_convergence displays graphics for more generations (2,4,6,10)

It is called in our main :

    NSGA_II(removeParameter="CostEx",show_convergence=True)
    NSGA_II(removeParameter="Reliability")
    NSGA_II(removeParameter="Latency")
    NSGA_II(show_convergence=True)
    NSGA_II()

