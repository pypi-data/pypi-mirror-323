import bluesky.preprocessors as bpp
import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i03
from dodal.common.beamlines.beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from dodal.devices.aperturescatterguard import (
    AperturePosition,
    ApertureScatterguard,
    load_positions_from_beamline_parameters,
)
from dodal.devices.s4_slit_gaps import S4SlitGaps
from dodal.devices.undulator import Undulator

from mx_bluesky.hyperion.device_setup_plans.read_hardware_for_setup import (
    read_hardware_during_collection,
    read_hardware_pre_collection,
)
from mx_bluesky.hyperion.parameters.constants import CONST


@pytest.mark.s03
async def test_getting_data_for_ispyb():
    params = GDABeamlineParameters.from_file(BEAMLINE_PARAMETER_PATHS["i03"])
    undulator = Undulator(
        f"{CONST.SIM.INSERTION_PREFIX}-MO-SERVC-01:",
        name="undulator",
        id_gap_lookup_table_path="/dls_sw/i03/software/daq_configuration/lookup/BeamLine_Undulator_toGap.txt",
    )
    synchrotron = i03.synchrotron(fake_with_ophyd_sim=True)
    slit_gaps = S4SlitGaps(f"{CONST.SIM.BEAMLINE}-AL-SLITS-04:", name="slits")
    attenuator = i03.attenuator(fake_with_ophyd_sim=True)
    flux = i03.flux(fake_with_ophyd_sim=True)
    dcm = i03.dcm(fake_with_ophyd_sim=True)
    aperture_scatterguard = ApertureScatterguard(
        prefix="BL03S",
        name="ap_sg",
        loaded_positions=load_positions_from_beamline_parameters(params),
        tolerances=AperturePosition.tolerances_from_gda_params(params),
    )
    smargon = i03.smargon(fake_with_ophyd_sim=True)
    eiger = i03.eiger(fake_with_ophyd_sim=True)
    await undulator.connect()
    await synchrotron.connect()
    await slit_gaps.connect()
    await attenuator.connect()
    await flux.connect()
    await aperture_scatterguard.connect()
    await smargon.connect()
    robot = i03.robot(fake_with_ophyd_sim=True)

    RE = RunEngine()

    @bpp.run_decorator()
    def standalone_read_hardware(und, syn, slits, robot, att, flux, ap_sg, sm):
        yield from read_hardware_pre_collection(und, syn, slits, dcm, smargon=sm)
        yield from read_hardware_during_collection(ap_sg, att, flux, dcm, eiger)

    RE(
        standalone_read_hardware(
            undulator,
            synchrotron,
            slit_gaps,
            robot,
            attenuator,
            flux,
            aperture_scatterguard,
            smargon,
        )
    )
