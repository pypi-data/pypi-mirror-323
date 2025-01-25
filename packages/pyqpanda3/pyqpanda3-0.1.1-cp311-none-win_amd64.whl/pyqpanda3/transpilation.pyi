class Transpiler:
    def __init__(self) -> None:
        """__init__(self: transpilation.Transpiler) -> None


                     @brief Default constructor for the Transpiler.
                     @details Initializes a new Transpiler instance.
             
        """
    def transpile(self, *args, **kwargs):
        """transpile(self: transpilation.Transpiler, prog: QPanda3::QProg, chip_topology_edges: list[list[int]] = [], init_mapping: dict[int, int] = {}, optimization_level: int = 2) -> QPanda3::QProg


                    @brief Transpile a quantum program.
                    @details This method transpiles a quantum program to fit the specified topology and optimization level.
                    @param[in] prog The quantum program to transpile.
                    @param[in] chip_topology_edges The topology of the chip.
                    @param[in] init_mapping Initial mapping from virtual qubits to physical qubits.
                    @param[in] optimization_level The level of optimization to apply.
                    @return The transpiled quantum program.
            
        """

def decompose(*args, **kwargs):
    """decompose(*args, **kwargs)
    Overloaded function.

    1. decompose(prog: QPanda3::QProg) -> QPanda3::QProg


              @brief Decompose a QProg into its constituent parts.
              @param[in] prog The QProg to decompose.
              @return The decomposed QProg.
          

    2. decompose(circuit: QPanda3::QCircuit) -> QPanda3::QCircuit


              @brief Decompose a QCircuit into its fundamental components.
              @param[in] circuit The QCircuit to decompose.
              @return The decomposed QCircuit.
          
    """
def generate_topology(num_qubit: int, topology_type: str) -> list[list[int]]:
    """generate_topology(num_qubit: int, topology_type: str) -> list[list[int]]


              @brief Generate the topology for quantum circuits.
              @details This function generates the topology based on the specified parameters.
          
    """
