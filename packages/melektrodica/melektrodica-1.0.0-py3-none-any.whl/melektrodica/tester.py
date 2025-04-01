"""

    μElektrodica© 2025
        by C. Baqueiro Basto, M. Secanell, L.C. Ordoñez
        is licensed under CC BY-NC-SA 4.0

        Tester class

"""

import numpy as np
from .grapher import Grapher


# for debugging
# import sys
# sys.exit()
# from .Tools import showme


class Tester:
    def __init__(self, data, results):
        self.print_species(data)
        self.print_coefficients(data)
        self.print_results(data, results)
        self.print_energies(data)

        # G = Grapher(data, results)
        # G.graph_results(data, results)

    def print_species(self, data):
        print(f"\nSPECIES: \n")
        print(f"Reactants, len {len(data.reactants)}:\n {data.reactants}")
        print(f"Products,  len {len(data.products)} :\n {data.products}")
        print(f"Adsorbed,  len {len(data.adsorbed)} :\n {data.adsorbed}")

    def print_coefficients(self, data):
        print(f"\nCOEFFICIENTS: \n")
        print(f"All coefficients, len {len(data.upsilon)}: \n {data.upsilon} \n")
        print(f"Species coefficients, len {len(data.upsilonx)}: \n {data.upsilonx} \n")
        print(f"Electrons number, len {len(data.ne)}: \n {data.ne} \n")

    def print_energies(selfself, data):
        print(f"\nENERGIES: \n")
        print(f"Activation Energies, len {len(data.Ga)}: \n {data.Ga} \n")
        print(f"Free Energies, len {len(data.DG)}: \n {data.DG} \n")

    def print_results(self, data, results):
        print(f"\nRESULTS: \n")
        print(
            f"Reactants concentrations, len {len(results.c_reactants)}: \n {results.c_reactants} \n"
        )
        print(
            f"Products concentrations, len {len(results.c_products)} : \n {results.c_products} \n"
        )
        print(f"Coverages, len {len(results.theta)}: \n {results.theta} \n ")
