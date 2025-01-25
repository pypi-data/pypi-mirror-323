import numpy as np
import uuid
import time

import astropy.units as u
from astropy.coordinates import SkyCoord, ICRS, AltAz
from iminuit import Minuit

from ctapipe.core import Component
from ctapipe.core.traits import (
    Float,
    Unicode,
    Int,
    List,
)

from ctapointing.config import from_config

DISTANCE_GOAL = (
    0.14  # distance goal for spot-star matching in pixels (tuned from chi2/dof)
)


class Leastsquares:

    errordef = Minuit.LEAST_SQUARES

    def __init__(
        self, model, image_solutions, nominal_pointing_altaz, lid_spots, camera
    ):
        self.model = model
        self.solutions = image_solutions
        self.nominal_pointing_altaz = nominal_pointing_altaz
        self.lid_spots = lid_spots

        self.pointing_camera = camera

        self.list_of_variables = []
        for name in model.parameters:
            self.list_of_variables.append(name)

        # make parameters known to iminuit
        self._parameters = {k: None for k in self.list_of_variables}

    @property
    def ndata(self):
        return len(self.solutions)

    def __call__(self, *par):
        chi2 = 0

        # set model parameters and calculate corrected pointing according to the model
        self.model.update_parameter_values(par)
        corrected_pointing_altaz = self.model.get_corrected_pointing(
            self.nominal_pointing_altaz
        )

        # project nominal pointing into camera, using corrected pointing as true telescope orientation
        # take care that each pointing is transformed with proper observation time information
        nominal_pointing = self.pointing_camera.project_into(
            self.nominal_pointing_altaz,
            telescope_pointing=corrected_pointing_altaz,
            use_obstime_of_first_coordinate=False,
        )
        nominal_pointing_pix = self.pointing_camera.transform_to_pixels(
            nominal_pointing
        )
        chi2 = np.sum((nominal_pointing_pix - self.lid_spots) ** 2) / DISTANCE_GOAL**2

        return chi2


class PointingModelFitter(Component):
    """
    Pointing model fitting class.
    """

    uuid = Unicode(
        default_value=str(uuid.uuid4()), help="UUID of PointingModelFitter"
    ).tag(config=True)
    name = Unicode(help="name of PointingModelFitter").tag(config=True)
    max_num_fit_iterations = Int(
        default_value=10, help="maximum number of fit iterations"
    ).tag(config=True)
    distance_goal = Float(default_value=0.1, help="fit distance goal").tag(config=True)
    fixed_parameters = List(
        default_value=[], help="list of parameters fixed during fitting"
    ).tag(config=True)
    residual_cut = Float(
        default_value=3.0, help="cut value for spot outlier removal"
    ).tag(config=True)

    def __str__(self):
        s = self.__repr__()
        return s

    def __repr__(self):
        return f"{self.__class__.__name__}" f"(uuid={self.uuid}, name={self.name})"

    @classmethod
    def from_config(cls, **kwargs):
        """
        Read a PointingModelFitter configuration from either configuration file or database.
        Either the path of a configuration file ('input_url') or a database collection
        ('collection') must be provided.


        Parameters
        ----------
        input_url: str or Path
            path of the configuration file.
        name: str
            name of the SpotExtractor (as in `SkyFitter.name`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct name is loaded.
            When loading from database, is used to identify the correct database record.
        uuid: str
            UUID of the camera (as in `PointingCamera.uuid`).
            When loading the configuration from file, can be set to check that the configuration with the
            correct UUID is loaded.
            When loading from database, is used to identify the correct database record.
        collection: str
            name of the database collection from which
            configuration is read
        database: str
            name of the database in which the collection
            is stored

        Returns
        -------
        fitter: PointingModelFitter object or None
        """
        # load configuration and construct instance
        config = from_config(component_name=cls.__name__, **kwargs)
        return cls(config=config)

    def process(self, model, solutions, camera):
        self.log.info(f"read {len(solutions)} image solutions.")

        nom_ra = [s.nominal_telescope_pointing_ra for s in solutions]
        nom_dec = [s.nominal_telescope_pointing_dec for s in solutions]
        mean_exp = [s.mean_exposure_time for s in solutions]

        nominal_pointing = SkyCoord(nom_ra, nom_dec, frame=ICRS)
        altaz = AltAz(
            location=camera.location,
            obstime=mean_exp,
            pressure=1020 * u.hPa,
            temperature=20 * u.deg_C,
        )
        nominal_pointing_altaz = nominal_pointing.transform_to(altaz)

        lid_spots = np.array([[s.lid_spots_x[0], s.lid_spots_y[0]] for s in solutions])

        start_fitting = time.perf_counter()

        lsq = Leastsquares(model, solutions, nominal_pointing_altaz, lid_spots, camera)
        m = Minuit(lsq, **model.get_parameters_as_dict(strip_units=True))

        for par in self.fixed_parameters:
            self.log.info(f"fixing parameter {par}")
            m.fixed[par] = True

        num_fits = 1
        # while num_fits <= self.max_num_fit_iterations:
        m.migrad()
        num_fits += 1

        stop_fitting = time.perf_counter()
        fitting_time = (stop_fitting - start_fitting) * u.s
        self.log.info(f"fitting time: {fitting_time:.2f}")

        return m
