import numpy as np
from darts.engines import operator_set_evaluator_iface, value_vector
from darts.physics.base.operators_base import OperatorsBase


class OperatorsGeothermal(OperatorsBase):
    def __init__(self, property_container, thermal: bool = True):
        super().__init__(property_container, thermal)


class acc_flux_custom_iapws_evaluator_python(OperatorsGeothermal):
    n_ops = 6

    def evaluate(self, state, values):
        pressure = state[0]
        pc = self.property
        pc.evaluate(state)

        pore_volume_factor = pc.rock_compaction_ev.evaluate(state)

        # mass accumulation
        values[0] = pore_volume_factor * np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph])
        # mass flux
        values[1] = np.sum(pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        # fluid internal energy = water_enthalpy + steam_enthalpy - work
        # (in the following expression, 100 denotes the conversion factor from bars to kJ/m3)
        values[2] = pore_volume_factor * (np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph] * pc.enthalpy[pc.ph])
                                          - 100 * pressure)
        # energy flux
        values[3] = np.sum(pc.enthalpy[pc.ph] * pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        # fluid conduction
        values[4] = np.sum(pc.conduction[pc.ph] * pc.saturation[pc.ph])
        # temperature
        values[5] = pc.temperature

        return 0


class acc_flux_custom_iapws_evaluator_python_well(OperatorsGeothermal):
    n_ops = 6

    def evaluate(self, state, values):
        pressure = state[0]
        pc = self.property
        pc.evaluate(state)

        pore_volume_factor = pc.rock_compaction_ev.evaluate(state)

        # mass accumulation
        values[0] = pore_volume_factor * np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph])
        # mass flux
        values[1] = np.sum(pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        # fluid internal energy = water_enthalpy + steam_enthalpy - work
        # (in the following expression, 100 denotes the conversion factor from bars to kJ/m3)
        values[2] = pore_volume_factor * (np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph] * pc.enthalpy[pc.ph])
                                          - 100 * pressure)
        # energy flux
        values[3] = np.sum(pc.enthalpy[pc.ph] * pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        # fluid conduction
        values[4] = 0.0
        # temperature
        values[5] = pc.temperature

        return 0


class acc_flux_gravity_evaluator_python(OperatorsGeothermal):
    n_ops = 10

    def evaluate(self, state, values):
        pressure = state[0]
        pc = self.property
        pc.evaluate(state)

        pore_volume_factor = pc.rock_compaction_ev.evaluate(state)

        # mass accumulation
        values[0] = pore_volume_factor * np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph])
        # mass flux
        values[1] = pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0] if 0 in pc.ph else 0.
        values[2] = pc.dens_m[1] * pc.relperm[1] / pc.viscosity[1] if 1 in pc.ph else 0.
        # fluid internal energy = water_enthalpy + steam_enthalpy - work
        # (in the following expression, 100 denotes the conversion factor from bars to kJ/m3)
        values[3] = pore_volume_factor * (np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph] * pc.enthalpy[pc.ph])
                                          - 100 * pressure)
        # energy flux
        values[4] = pc.enthalpy[0] * pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0] if 0 in pc.ph else 0.
        values[5] = pc.enthalpy[1] * pc.dens_m[1] * pc.relperm[1] / pc.viscosity[1] if 1 in pc.ph else 0.
        # fluid conduction
        values[6] = np.sum(pc.conduction[pc.ph] * pc.saturation[pc.ph])
        # water density
        values[7] = pc.dens_m[0] if 0 in pc.ph else 0.
        # steam density
        values[8] = pc.dens_m[1] if 1 in pc.ph else 0.
        # temperature
        values[9] = pc.temperature

        return 0


class acc_flux_gravity_evaluator_python_well(OperatorsGeothermal):
    n_ops = 10

    def evaluate(self, state, values):
        pressure = state[0]
        pc = self.property
        pc.evaluate(state)

        pore_volume_factor = pc.rock_compaction_ev.evaluate(state)

        # mass accumulation
        values[0] = pore_volume_factor * np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph])
        # mass flux
        values[1] = pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0] if 0 in pc.ph else 0.
        values[2] = pc.dens_m[1] * pc.relperm[1] / pc.viscosity[1] if 1 in pc.ph else 0.
        # fluid internal energy = water_enthalpy + steam_enthalpy - work
        # (in the following expression, 100 denotes the conversion factor from bars to kJ/m3)
        values[3] = pore_volume_factor * (np.sum(pc.dens_m[pc.ph] * pc.saturation[pc.ph] * pc.enthalpy[pc.ph])
                                          - 100 * pressure)
        # energy flux
        values[4] = pc.enthalpy[0] * pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0] if 0 in pc.ph else 0.
        values[5] = pc.enthalpy[1] * pc.dens_m[1] * pc.relperm[1] / pc.viscosity[1] if 1 in pc.ph else 0.
        # fluid conduction
        values[6] = 0.0
        # water density
        values[7] = pc.dens_m[0] if 0 in pc.ph else 0.
        # steam density
        values[8] = pc.dens_m[1] if 1 in pc.ph else 0.
        # temperature
        values[9] = pc.temperature

        return 0


class geothermal_rate_custom_evaluator_python(OperatorsGeothermal):
    n_ops = 4

    def evaluate(self, state, values):
        pc = self.property
        pc.evaluate(state)

        total_density = np.sum(pc.saturation[pc.ph] * pc.dens_m[pc.ph])
        total_flux = np.sum(pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph]) / total_density

        # water volumetric rate
        values[0] = pc.saturation[0] * total_flux if 0 in pc.ph else 0.
        # steam volumetric rate
        values[1] = pc.saturation[1] * total_flux if 1 in pc.ph else 0.
        # temperature
        values[2] = pc.temperature
        # energy rate
        values[3] = np.sum(pc.enthalpy[pc.ph] * pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])

        return 0


class geothermal_mass_rate_custom_evaluator_python(OperatorsGeothermal):
    n_ops = 4

    def evaluate(self, state, values):
        pc = self.property
        pc.evaluate(state)

        total_density = np.sum(pc.saturation[pc.ph] * pc.dens_m[pc.ph])

        # water mass rate
        values[0] = np.sum(pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        # steam mass rate
        values[1] = pc.saturation[1] * (pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0]
                                        + pc.dens_m[0] * pc.relperm[0] / pc.viscosity[0]) / total_density
        # temperature
        values[2] = pc.temperature
        # energy rate
        values[3] = np.sum(pc.enthalpy[pc.ph] * pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])
        
        return 0

class MassFluxOperators(OperatorsGeothermal):
    n_ops = 1

    def evaluate(self, state, values):
        pc = self.property
        pc.evaluate(state)

        """ Beta operator here represents mass flux term: """
        values[0] = np.sum(pc.dens_m[pc.ph] * pc.relperm[pc.ph] / pc.viscosity[pc.ph])

        return 0
