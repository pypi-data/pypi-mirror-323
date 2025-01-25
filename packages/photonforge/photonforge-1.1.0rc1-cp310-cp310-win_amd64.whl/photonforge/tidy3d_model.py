from .extension import (
    Component,
    PortSpec,
    Port,
    FiberPort,
    GaussianPort,
    Model,
    SMatrix,
    Technology,
    register_model_class,
    Z_MAX,
    config,
    snap_to_grid,
    frequency_classification,
)
from .utils import C_0, _filename_cleanup, _safe_hash
from .cache import _cache_path, _mode_solver_cache, _tidy3d_model_cache, cache_s_matrix

import numpy
import pydantic
import tidy3d
from tidy3d.plugins.mode import ModeSolver
from tidy3d.components.data.data_array import ScalarModeFieldDataArray

import collections
import copy as libcopy
import json
import os
import pathlib
import time
import tempfile
import warnings
import zlib
from typing import Any, Optional, Union
from collections.abc import Sequence

_Medium = tidy3d.components.medium.MediumType
_MonitorData = tidy3d.components.data.monitor_data.MonitorData
_ElectromagneticFieldData = tidy3d.components.data.monitor_data.ElectromagneticFieldData

# Polling interval for Tidy3D tasks
TIDY3D_POLLING_INTERVAL: float = 1.0

# Overlap threshold to discard modes in symmetry mapping
OVERLAP_THRESHOLD: float = 0.1

use_local_mode_solver: bool = False

_pending_tasks: set = set()


def abort_pending_tasks() -> list[str]:
    """Abort all known pending Tidy3D pending tasks.

    Returns:
        List of aborted task ids.
    """
    from tidy3d.web.api.webapi import abort
    from tidy3d.web.core.exceptions import WebError

    result = list(_pending_tasks)
    while len(_pending_tasks) > 0:
        task_id = _pending_tasks.pop()
        try:
            abort(task_id)
        except WebError:
            pass
    return result


def _tidy3d_to_bytes(obj: tidy3d.components.base.Tidy3dBaseModel) -> bytes:
    tmp_file, tmp_name = tempfile.mkstemp(".hdf5")
    os.close(tmp_file)
    tmp_file = pathlib.Path(tmp_name)
    sim_bytes = None
    try:
        obj.to_hdf5(tmp_name)
        sim_bytes = tmp_file.read_bytes()
    finally:
        tmp_file.unlink()
    return sim_bytes


def _convert_arrays(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, dict):
            _convert_arrays(v)
        elif isinstance(v, numpy.ndarray):
            d[k] = v.tolist()
    return d


def _weighted_coord_max(
    array: numpy.ndarray, u: numpy.ndarray, v: numpy.ndarray
) -> tuple[int, int]:
    m = array * u.reshape(-1, 1)
    i = numpy.arange(array.shape[0])
    i = int(0.5 + (m * i.reshape(-1, 1)).sum() / m.sum())
    m = array * v
    j = numpy.arange(array.shape[1])
    j = int(0.5 + (m * j).sum() / m.sum())
    return i, j


def _mode_normalization_signs(mode_data: _MonitorData) -> list[int]:
    fields = mode_data.field_components
    coords = fields["Ez"].coords

    normal = mode_data.monitor.size.index(0)
    dirs = ["x", "y", "z"]
    dirs.pop(normal)

    du = numpy.diff(numpy.pad(coords[dirs[0]].values, 1, "edge"))
    dv = numpy.diff(numpy.pad(coords[dirs[1]].values, 1, "edge"))
    du = 0.5 * (du[1:] + du[:-1])
    dv = 0.5 * (dv[1:] + dv[:-1])

    num_modes = 1
    isel = {"f": coords["f"].size // 2}
    if "mode_index" in coords:
        num_modes = coords["mode_index"].values.size
        isel["mode_index"] = 0

    signs = [0] * num_modes
    for mode_index in range(num_modes):
        if "mode_index" in isel:
            isel["mode_index"] = mode_index
        e = fields["E" + dirs[0]].isel(**isel).values.real.squeeze()
        e2 = fields["E" + dirs[1]].isel(**isel).values.real.squeeze()
        if e.ndim == 1:  # Fields from a 2D simulation
            e = e.reshape((du.size, dv.size))
            e2 = e2.reshape((du.size, dv.size))
        abs_e = numpy.abs(e)
        abs_e2 = numpy.abs(e2)
        if abs_e2.max() > abs_e.max():
            e = e2
            abs_e = abs_e2
        e2 = abs_e**2
        i, j = e.shape
        while signs[mode_index] == 0 and i > 0 and j > 0:
            if (e[:i, :j] > 0).all():
                signs[mode_index] = 1
            elif (e[:i, :j] < 0).all():
                signs[mode_index] = -1
            else:
                threshold = abs_e[:i, :j].max() * 0.5
                i, j = _weighted_coord_max(e2[:i, :j], du[:i], dv[:j])
                if e[i, j] >= threshold:
                    signs[mode_index] = 1
                elif e[i, j] <= -threshold:
                    signs[mode_index] = -1
        if signs[mode_index] == 0:
            warnings.warn(
                f"Mode normalization failed for mode index {mode_index}. "
                "Consider increasing the mesh refinement for the mode solver.",
                RuntimeWarning,
                2,
            )
            signs[mode_index] = 1.0

    return signs


def _align_and_overlap(data0: _MonitorData, data1: _MonitorData) -> numpy.ndarray:
    rotations = [(0, "+"), (1, "+"), (0, "-"), (1, "-")]
    dir0 = getattr(data0.monitor, "direction", None)
    if dir0 is None:
        dir0 = data0.monitor.store_fields_direction
    dir1 = getattr(data1.monitor, "direction", None)
    if dir1 is None:
        dir1 = data1.monitor.store_fields_direction
    r0 = rotations.index((data0.monitor.size.index(0), dir0))
    r1 = rotations.index((data1.monitor.size.index(0), dir1))
    rotation = (r1 - r0) % 4

    fields0 = data0.field_components
    fields1 = data1.field_components

    dims = fields0["Ez"].dims
    coords = {d: fields0["Ez"].coords[d].values.copy() for d in dims}
    center = (data0.monitor.center[0], data0.monitor.center[1])

    if rotation == 0:
        fields0 = {
            "Ex": fields0["Ex"].values,
            "Hx": fields0["Hx"].values,
            "Ey": fields0["Ey"].values,
            "Hy": fields0["Hy"].values,
            "Ez": fields0["Ez"].values,
            "Hz": fields0["Hz"].values,
        }
    elif rotation == 1:
        x = coords["x"]
        coords["x"] = -coords["y"]
        coords["y"] = x
        center = (-center[1], center[0])
        ix = dims.index("x")
        iy = dims.index("y")
        fields0 = {
            "Ex": numpy.swapaxes(-fields0["Ey"].values, ix, iy),
            "Hx": numpy.swapaxes(-fields0["Hy"].values, ix, iy),
            "Ey": numpy.swapaxes(fields0["Ex"].values, ix, iy),
            "Hy": numpy.swapaxes(fields0["Hx"].values, ix, iy),
            "Ez": numpy.swapaxes(fields0["Ez"].values, ix, iy),
            "Hz": numpy.swapaxes(fields0["Hz"].values, ix, iy),
        }
    elif rotation == 2:
        coords["x"] = -coords["x"]
        coords["y"] = -coords["y"]
        center = (-center[0], -center[1])
        fields0 = {
            "Ex": -fields0["Ex"].values,
            "Hx": -fields0["Hx"].values,
            "Ey": -fields0["Ey"].values,
            "Hy": -fields0["Hy"].values,
            "Ez": fields0["Ez"].values,
            "Hz": fields0["Hz"].values,
        }
    elif rotation == 3:
        x = coords["x"]
        coords["x"] = coords["y"]
        coords["y"] = -x
        center = (center[1], -center[0])
        ix = dims.index("x")
        iy = dims.index("y")
        fields0 = {
            "Ex": numpy.swapaxes(fields0["Ey"].values, ix, iy),
            "Hx": numpy.swapaxes(fields0["Hy"].values, ix, iy),
            "Ey": numpy.swapaxes(-fields0["Ex"].values, ix, iy),
            "Hy": numpy.swapaxes(-fields0["Hx"].values, ix, iy),
            "Ez": numpy.swapaxes(fields0["Ez"].values, ix, iy),
            "Hz": numpy.swapaxes(fields0["Hz"].values, ix, iy),
        }

    coords["x"] = coords["x"] + data1.monitor.center[0] - center[0]
    coords["y"] = coords["y"] + data1.monitor.center[1] - center[1]

    n, t = ("x", "y") if r1 % 2 == 0 else ("y", "x")
    tangential_components = ("E" + t, "H" + t, "Ez", "Hz")
    fields0 = {
        c: ScalarModeFieldDataArray(fields0[c], dims=dims, coords=coords)
        for c in tangential_components
    }

    coords1 = tidy3d.Coords(
        x=fields1["Ez"].coords["x"].values,
        y=fields1["Ez"].coords["y"].values,
        z=fields1["Ez"].coords["z"].values,
    )
    fields0 = {c: coords1.spatial_interp(fields0[c], "linear") for c in tangential_components}

    if "mode_index" in dims:
        sign0 = numpy.array(_mode_normalization_signs(data0))
        fields0 = {k: v * sign0 for k, v in fields0.items()}
        sign1 = numpy.array(_mode_normalization_signs(data1))
        fields1 = {k: v * sign1 for k, v in fields1.items()}

    sign = -1 if r1 == 1 or r1 == 2 else 1
    d_area = sign * data1._diff_area
    e0_h1 = fields0["E" + t] * fields1["Hz"] - fields0["Ez"] * fields1["H" + t]
    e1_h0 = fields1["E" + t] * fields0["Hz"] - fields1["Ez"] * fields0["H" + t]
    integrand = (e0_h1 + e1_h0) * d_area
    overlap = 0.25 * integrand.sum(dim=d_area.dims).isel({n: 0}, drop=True).values

    # Modes are normalized by the mode solver, so the overlap should be only a phase difference.
    # We normalize the result to remove numerical errors introduced by the grid interpolation.
    overlap_mag = numpy.abs(overlap)
    if not numpy.allclose(overlap_mag, 1.0, atol=0.1):
        max_err = overlap_mag.flat[numpy.argmax(numpy.abs(overlap_mag - 1.0))]
        warnings.warn(
            f"Modal overlap calculation resulted in an unexpected magnitude ({max_err}). Consider "
            "increasing the mesh refinement for the mode solver.",
            RuntimeWarning,
            2,
        )

    return overlap / overlap_mag


def _align_and_overlap_analytical(port0: GaussianPort, port1: GaussianPort) -> float:
    # NOTE: use any frequency and medium here because they should not matter
    frequencies = [C_0]
    center0, size0, direction0, _, _ = port0._axis_aligned_properties(frequencies)
    center1, size1, direction1, _, _ = port0._axis_aligned_properties(frequencies)
    _, _, _, e0_pol, h0_pol = port0.fields(*center0, frequencies)
    _, _, _, e1_pol, h1_pol = port1.fields(*center1, frequencies)

    if direction0 == 2 or direction1 == 2:
        if direction0 != 2 or direction1 != 2 or direction0 != direction1:
            raise RuntimeError("Unexpected rotation for GaussianPort in reference.")
        return 1.0

    if abs(e0_pol[2]) > abs(h0_pol[2]):
        z0 = e0_pol[2]
        z1 = e0_pol[2]
    else:
        z0 = h0_pol[2]
        z1 = h0_pol[2]
    return 1.0 if (z0 > 0) == (z1 > 0) else -1.0


class _Tidy3DTaskRunner:
    def __init__(
        self,
        simulation: Union[tidy3d.Simulation, tidy3d.EMESimulation],
        task_name: str,
        remote_path: str,
        data_path: str,
        verbose: bool,
    ) -> None:
        from tidy3d import web

        self.type = "fdtd"
        if isinstance(simulation, tidy3d.EMESimulation):
            self.type = "eme"
        self.simulation = simulation
        self.task_name = task_name
        self.remote_path = remote_path
        self.data_path = data_path
        self.verbose = verbose
        self.task_id = None
        self._data = None
        self._next_status = time.monotonic()
        self._suffix = _safe_hash(
            _tidy3d_to_bytes(simulation) + task_name.encode("utf-8") + remote_path.encode("utf-8")
        )

        self.data_path.mkdir(parents=True, exist_ok=True)

        # Use cached data, if available
        info_file = self.info_file()
        sim_file = self.sim_file()
        data_file = self.data_file()
        if info_file.is_file() and sim_file.is_file() and data_file.is_file():
            info = json.loads(info_file.read_text())
            if (
                self.task_name == info["task_name"]
                and self.remote_path == info["remote_path"]
                and str(self.data_path) == info["data_path"]
            ):
                if verbose:
                    print(f"Loading cached simulation from {str(info_file)}.")
                self.task_id = info["task_id"]
                self._data = (
                    tidy3d.SimulationData.from_file(str(data_file))
                    if self.type == "fdtd"
                    else tidy3d.EMESimulationData.from_file(str(data_file))
                )
                self._status = {
                    "progress": 100,
                    "message": "success",
                    "tasks": [{"task_id": self.task_id}],
                }
                return

        self.task_id = web.upload(
            simulation,
            task_name,
            folder_name=remote_path,
            verbose=verbose,
            simulation_type="photonforge",
        )
        self._status = {
            "progress": 0,
            "message": "running",
            "tasks": [{"task_id": self.task_id}],
        }
        web.start(self.task_id)
        _pending_tasks.add(self.task_id)

    def info_file(self) -> pathlib.Path:
        return self.data_path / f"{self.type}_info-{self._suffix}.json"

    def sim_file(self) -> pathlib.Path:
        return self.data_path / f"{self.type}-{self._suffix}.hdf5"

    def data_file(self) -> pathlib.Path:
        return self.data_path / f"{self.type}_data-{self._suffix}.hdf5"

    @property
    def status(self) -> dict[str, Any]:
        from tidy3d import web
        from tidy3d.web.api import webapi

        now = time.monotonic()
        if now >= self._next_status and self._status["message"] == "running":
            from tidy3d.web.core.exceptions import WebError

            try:
                info = web.get_info(self.task_id, verbose=False)
            except WebError:
                info = None
            if (
                info is None
                or info.status in ("error", "diverged", "deleted")
                or info.status.startswith("abort")  # aborting, aborted
            ):
                if info is not None:
                    warnings.warn(
                        f"Task with taskId={self.task_id} returned status '{info.status}'."
                    )
                    _pending_tasks.discard(self.task_id)
                message = "error"
                progress = 100
            elif info.status == "success":
                message = "success"
                progress = 100
                _pending_tasks.discard(self.task_id)
            else:
                message = "running"
                run_info = webapi.get_run_info(self.task_id)
                progress = run_info[0]

            self._status = {
                "progress": progress,
                "message": message,
                "tasks": [{"task_id": self.task_id}],
            }
            self._next_status = now + TIDY3D_POLLING_INTERVAL
            if message == "success":
                _ = self.data
        return self._status

    @property
    def data(self) -> Union[tidy3d.SimulationData, tidy3d.EMESimulationData]:
        if self._data is None:
            from tidy3d import web

            if self.status["message"] != "success":
                raise RuntimeError(
                    f"Tidy3D task with taskId={self.task_id} did not complete successfully."
                )

            info = {
                "task_id": self.task_id,
                "task_name": self.task_name,
                "remote_path": self.remote_path,
                "data_path": str(self.data_path),
            }
            self.info_file().write_text(json.dumps(info))

            sim_file = self.sim_file()
            if not sim_file.is_file():
                self.simulation.to_hdf5(str(sim_file))

            self._data = web.load(self.task_id, str(self.data_file()), verbose=self.verbose)
        return self._data


class _ModeSolverTaskRunner:
    def __init__(
        self,
        mode_solver: ModeSolver,
        task_name: str,
        remote_path: str,
        data_path: str,
        verbose: bool,
    ) -> None:
        from tidy3d.web.api.mode import ModeSolverTask

        self.mode_solver = mode_solver
        self.task_name = task_name
        self.remote_path = remote_path
        self.data_path = pathlib.Path(data_path).expanduser()
        self.verbose = verbose
        self.task = None
        self._data = None
        self._next_status = time.monotonic()
        self._suffix = _safe_hash(
            _tidy3d_to_bytes(mode_solver) + task_name.encode("utf-8") + remote_path.encode("utf-8")
        )

        self.data_path.mkdir(parents=True, exist_ok=True)

        # Use cached data, if available
        info_file = self.info_file()
        sim_file = self.sim_file()
        data_file = self.data_file()
        if info_file.is_file() and sim_file.is_file() and data_file.is_file():
            info = json.loads(info_file.read_text())
            if (
                self.task_name == info["task_name"]
                and self.remote_path == info["remote_path"]
                and str(self.data_path) == info["data_path"]
            ):
                if verbose:
                    print(f"Loading cached simulation from {str(info_file)}.")
                task_id = info["task_id"]
                solver_id = info["solver_id"]
                self.task = ModeSolverTask(
                    task_id=task_id,
                    solver_id=solver_id,
                    status="success",
                    file_type="Gz",
                    mode_solver=mode_solver,
                )
                self._data = tidy3d.ModeSolverData.from_file(str(data_file))
                self._status = {
                    "progress": 100,
                    "message": "success",
                    "tasks": [{"task_id": task_id, "solver_id": solver_id}],
                }
                return

        self.task = ModeSolverTask.create(
            mode_solver=mode_solver,
            task_name=task_name,
            folder_name=remote_path,
        )
        self._status = {
            "progress": 0,
            "message": "running",
            "tasks": [{"task_id": self.task.task_id, "solver_id": self.task.solver_id}],
        }
        self.task.upload(verbose=self.verbose)
        self.task.submit()
        _pending_tasks.add(self.task.task_id)

    def info_file(self) -> pathlib.Path:
        return self.data_path / f"ms_info-{self._suffix}.json"

    def sim_file(self) -> pathlib.Path:
        return self.data_path / f"ms-{self._suffix}.hdf5"

    def data_file(self) -> pathlib.Path:
        return self.data_path / f"ms_data-{self._suffix}.hdf5"

    @property
    def status(self) -> dict[str, Any]:
        now = time.monotonic()
        if now >= self._next_status and self._status["message"] == "running":
            from tidy3d.web.core.exceptions import WebError

            try:
                info = self.task.get_info()
            except WebError:
                info = None
            if (
                info is None
                or info.status in ("error", "diverged", "deleted")
                or info.status.startswith("abort")  # aborting, aborted
            ):
                if info is not None:
                    warnings.warn(
                        f"Task with taskId={self.task.task_id} returned status '{info.status}'."
                    )
                    _pending_tasks.discard(self.task.task_id)
                message = "error"
                progress = 100
            elif info.status == "success":
                message = "success"
                progress = 100
                _pending_tasks.discard(self.task.task_id)
            else:
                message = "running"
                progress = 0 if info == "queued" else 50

            self._status = {
                "progress": progress,
                "message": message,
                "tasks": [{"task_id": self.task.task_id, "solver_id": self.task.solver_id}],
            }
            self._next_status = now + TIDY3D_POLLING_INTERVAL
            if message == "success":
                _ = self.data
        return self._status

    @property
    def data(self) -> tidy3d.ModeSolverData:
        if self._data is None:
            if self.status["message"] != "success":
                raise RuntimeError(
                    f"Tidy3D ModeSolver task with taskId={self.task.task_id} "
                    f"solverId={self.task.solver_id} did not complete successfully."
                )

            info = {
                "task_id": self.task.task_id,
                "solver_id": self.task.solver_id,
                "task_name": self.task_name,
                "remote_path": self.remote_path,
                "data_path": str(self.data_path),
            }
            self.info_file().write_text(json.dumps(info))

            sim_file = self.sim_file()
            if not sim_file.is_file():
                self.mode_solver.to_hdf5(str(sim_file))

            self._data = self.task.get_result(to_file=str(self.data_file()), verbose=self.verbose)
        return self._data


def _simulation_runner(
    *,
    simulation: Union[tidy3d.Simulation, tidy3d.EMESimulation, ModeSolver],
    task_name: str,
    remote_path: str,
    data_path: str,
    verbose: bool,
) -> Any:
    if simulation.type == "Simulation" or simulation.type == "EMESimulation":
        return _Tidy3DTaskRunner(simulation, task_name, remote_path, data_path, verbose)
    elif simulation.type == "ModeSolver":
        if use_local_mode_solver:
            old_level = tidy3d.config.logging_level
            tidy3d.config.logging_level = "ERROR"
            data = simulation.solve()
            tidy3d.config.logging_level = old_level
            RunnerResult = collections.namedtuple("RunnerResult", ("status", "data"))
            return RunnerResult(status={"progress": 100, "message": "success"}, data=data)
        else:
            return _ModeSolverTaskRunner(simulation, task_name, remote_path, data_path, verbose)
    else:
        raise TypeError("Argument 'simulation' must be a Tidy3D Simulation or ModeSolver.")


class _ModeSolverRunner:
    def __init__(
        self,
        port: Union[Port, FiberPort, PortSpec],
        frequencies: Sequence[float],
        mesh_refinement: float,
        technology: Technology,
        task_name: Optional[str] = None,
        remote_path: str = "Mode Solver",
        verbose: bool = True,
        center_in_origin: bool = True,
    ) -> None:
        if mesh_refinement is None:
            mesh_refinement = config.default_mesh_refinement

        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)

        if isinstance(port, Port):
            if center_in_origin:
                port = port.copy()
                port.center = (0, 0)
            mode_solver = port.to_tidy3d_mode_solver(
                frequencies, mesh_refinement, technology=technology
            )
            description = port.spec.description
        elif isinstance(port, FiberPort):
            if center_in_origin:
                port = port.copy()
                port.center = (0, 0, 0)
            mode_solver = port.to_tidy3d_mode_solver(
                frequencies, mesh_refinement, technology=technology
            )
            description = "FiberPort"
        elif isinstance(port, PortSpec):
            mode_solver = port.to_tidy3d(frequencies, mesh_refinement, technology=technology)
            description = port.description
        else:
            raise TypeError("'port' must be a Port, FiberPort, or PortSpec instance.")

        mode_solver_bytes = _tidy3d_to_bytes(mode_solver)
        key = (mode_solver_bytes, remote_path)
        self.runner = _mode_solver_cache[key]
        if self.runner is None or self.runner.status["message"] == "error":
            suffix = _safe_hash(mode_solver_bytes)
            if task_name is None:
                task_name = _filename_cleanup("Mode-" + description)
            self.runner = _simulation_runner(
                simulation=mode_solver,
                task_name=task_name,
                remote_path=remote_path,
                data_path=_cache_path(suffix),
                verbose=verbose,
            )
            _mode_solver_cache[key] = self.runner

    @property
    def status(self) -> dict[str, Any]:
        return self.runner.status

    @property
    def data(self) -> Union[tidy3d.SimulationData, tidy3d.ModeSolverData]:
        return self.runner.data


def _inner_product(
    field_data: _ElectromagneticFieldData,
    port: GaussianPort,
    epsilon_r: float,
    conjugate: bool = True,
) -> numpy.ndarray:
    normal = field_data.monitor.size.index(0)

    freqs = field_data.Ex.coords["f"].values
    x = field_data.Ex.coords["x"].values
    y = field_data.Ex.coords["y"].values
    z = field_data.Ex.coords["z"].values

    shape = [x.size, y.size, z.size]
    shape.pop(normal)
    shape = tuple(shape) + (freqs.size,)

    dim_names = ["x", "y", "z", "f"]
    dim_names.pop(normal)

    dims = [0, 1, 2]
    dims.pop(normal)

    d_area = field_data._diff_area.transpose(*dim_names[:-1]).values

    fields_a = field_data._colocated_tangential_fields
    ea = (
        fields_a["E" + dim_names[0]].transpose(*dim_names).values,
        fields_a["E" + dim_names[1]].transpose(*dim_names).values,
    )
    ha = (
        fields_a["H" + dim_names[0]].transpose(*dim_names).values,
        fields_a["H" + dim_names[1]].transpose(*dim_names).values,
    )

    del fields_a

    # This comes from ElectromagneticFieldData._tangential_corrected()
    if normal == 1:
        ha = (-ha[0], -ha[1])

    x, y, z = numpy.meshgrid(x, y, z, indexing="ij")
    field_profile, e0, h0, e_pol, h_pol = port.fields(
        x.flatten(), y.flatten(), z.flatten(), freqs, epsilon_r
    )
    del x, y, z

    field_profile = field_profile.reshape(shape)
    if conjugate:
        field_profile = field_profile.conj()

    e_x_h = field_profile * (
        h0 * (h_pol[dims[1]] * ea[0] - h_pol[dims[0]] * ea[1])
        + e0 * (e_pol[dims[0]] * ha[1] - e_pol[dims[1]] * ha[0])
    )

    return 0.25 * (d_area[..., numpy.newaxis] * e_x_h).sum((0, 1))


def _get_amps(
    data: _ElectromagneticFieldData,
    port: Union[Port, FiberPort, GaussianPort],
    epsilon_r: float,
    mode_index: int,
    reversed: bool,
) -> numpy.ndarray:
    if isinstance(port, (Port, FiberPort)):
        _, _, direction, *_ = port._axis_aligned_properties()
        direction = "-" if (direction == "+") == reversed else "+"
        amps = data.amps.sel(direction=direction, mode_index=mode_index).values.flatten()
        return amps

    if reversed:
        port = port.reflected()
    return _inner_product(data, port, epsilon_r)


def _mode_remap_from_symmetry(
    elements: dict[str, numpy.ndarray],
    ports: dict[str, Union[Port, GaussianPort]],
    data_sym: dict[str, Union[tidy3d.ModeData, tidy3d.ModeSolverData]],
    data_full: dict[str, Union[tidy3d.ModeData, tidy3d.ModeSolverData]],
):
    num_freqs = next(iter(elements.values())).size
    mode_names = [
        f"{name}@{index}" for name, port in sorted(ports.items()) for index in range(port.num_modes)
    ]

    # Port mode transformation matrix
    # M_ij = <e_i, e_j'> / <e_i, e_i>
    # S' = pinv(M) × S × M
    s = numpy.zeros((num_freqs, len(mode_names), len(mode_names)), dtype=complex)
    m = numpy.zeros((num_freqs, len(mode_names), len(mode_names)), dtype=complex)

    for j, mode_in in enumerate(mode_names):
        for i, mode_out in enumerate(mode_names):
            element = elements.get((mode_in, mode_out), None)
            if element is not None:
                s[:, i, j] = element

    total_modes = 0
    total_columns = 0
    invalid_sym_modes = []
    for name, port in sorted(ports.items()):
        num_modes = port.num_modes
        if isinstance(port, GaussianPort):
            m[
                :, total_modes : total_modes + num_modes, total_columns : total_columns + num_modes
            ] = numpy.eye(num_modes, dtype=complex)
            total_columns += num_modes
        else:
            sym_mode = data_sym[name]
            full_mode = data_full[name]
            projection = sym_mode.outer_dot(full_mode, conjugate=False)
            norm = sym_mode.dot(sym_mode, conjugate=False)
            # TODO: ModeMonitor fields have incorrect normalizations. This is a temporary workaround.
            # norm[:] = 1
            m_block = (
                projection.transpose("mode_index_1", "mode_index_0", "f").values
                / norm.transpose("mode_index", "f").values
            ).T
            for sym_index in range(num_modes):
                m_line = m_block[:, sym_index, :num_modes]
                if (
                    numpy.sqrt((numpy.abs(m_line) ** 2).sum(axis=1)).sum()
                    < OVERLAP_THRESHOLD * num_freqs
                ):
                    invalid_sym_modes.append(total_modes + sym_index)
            for full_index in range(num_modes):
                m_column = m_block[:, :num_modes, full_index]
                if (
                    numpy.sqrt((numpy.abs(m_column) ** 2).sum(axis=1)).sum()
                    < OVERLAP_THRESHOLD * num_freqs
                ):
                    mode_names.pop(total_columns)
                else:
                    m[:, total_modes : total_modes + num_modes, total_columns] = m_column
                    total_columns += 1
        total_modes += num_modes

    m = m[:, :, :total_columns]
    if len(invalid_sym_modes) > 0:
        m = numpy.delete(m, invalid_sym_modes, 1)
        s = numpy.delete(s, invalid_sym_modes, 1)
        s = numpy.delete(s, invalid_sym_modes, 2)

    s = numpy.linalg.pinv(m) @ s @ m
    return {
        (mode_in, mode_out): s[:, i, j]
        for j, mode_in in enumerate(mode_names)
        for i, mode_out in enumerate(mode_names)
    }


class _Tidy3DModelRunner:
    def __init__(
        self,
        frequencies: Sequence[float],
        simulations: tidy3d.Simulation,
        ports: dict[str, Union[Port, FiberPort, GaussianPort]],
        port_epsilon: dict[str, float],
        element_mappings: dict[tuple[str, str], tuple[str, str]],
        folder_name: str,
        data_path: str,
        batch_file: str,
        verbose: bool,
    ) -> None:
        from tidy3d.web import BatchData

        self.mode_data_key = sorted(simulations)[0]
        self.frequencies = frequencies
        self.runners = {}
        for name, sim in simulations.items():
            key = (_tidy3d_to_bytes(sim), folder_name, data_path)
            runner = _tidy3d_model_cache[key]
            if runner is None or runner.status["message"] == "error":
                runner = _simulation_runner(
                    simulation=sim,
                    task_name=name,
                    remote_path=folder_name,
                    data_path=data_path,
                    verbose=verbose,
                )
                _tidy3d_model_cache[key] = runner
            self.runners[name] = runner

        self.ports = ports
        self.port_epsilon = port_epsilon
        self.element_mappings = element_mappings
        self._s_matrix = None

        # Store batch data for later use
        task_paths = {}
        task_ids = {}
        for name, runner in self.runners.items():
            if isinstance(runner, _Tidy3DTaskRunner):
                task_paths[name] = str(runner.data_file())
                task_ids[name] = runner.task_id
        if len(task_ids) > 0:
            batch = BatchData(task_paths=task_paths, task_ids=task_ids, verbose=verbose)
            batch.to_file(str(batch_file))

        # If the model uses any symmetry, it will impact the mode numbering of the ports.
        # We need to remap port modes from the symmetry-applied to the full version.
        # The first simulation contains all mode fields with symmetry, so we only need to
        # solve for the modes in the for full version.
        full_sim = simulations[self.mode_data_key]
        if full_sim.symmetry != (0, 0, 0):
            full_sim = full_sim.copy(update={"symmetry": (0, 0, 0)})
            for monitor in full_sim.monitors:
                if not isinstance(monitor, tidy3d.ModeMonitor):
                    continue
                mode_solver = ModeSolver(
                    simulation=full_sim,
                    plane=monitor.bounding_box,
                    mode_spec=monitor.mode_spec,
                    freqs=monitor.freqs,
                    direction=monitor.store_fields_direction,
                )
                self.runners[monitor.name] = _simulation_runner(
                    simulation=mode_solver,
                    task_name=monitor.name,
                    remote_path=folder_name,
                    data_path=data_path,
                    verbose=verbose,
                )

    @property
    def status(self) -> dict[str, Any]:
        """Monitor S matrix computation progress."""
        all_stat = [runner.status for runner in self.runners.values()]
        if all(s["message"] == "success" for s in all_stat):
            message = "success"
            progress = 100
        elif any(s["message"] == "error" for s in all_stat):
            message = "error"
            progress = 100
        else:
            message = "running"
            progress = sum(
                100 if s["message"] == "success" else s["progress"] for s in all_stat
            ) / len(all_stat)
        return {"progress": progress, "message": message}

    @property
    def s_matrix(self) -> SMatrix:
        """Get the model S matrix."""
        if self._s_matrix is None:
            # Get mode field data from the first simulation and compute normalizations
            mode_data = self.runners[self.mode_data_key].data
            mode_norm = {name: _mode_normalization_signs(mode_data[name]) for name in self.ports}

            elements = {}
            for src, src_port in self.ports.items():
                for src_mode in range(src_port.num_modes):
                    src_key = f"{src}@{src_mode}"
                    if src_key not in self.runners:
                        continue
                    data = self.runners[src_key].data
                    norm = mode_norm[src][src_mode] * _get_amps(
                        data[src], src_port, self.port_epsilon.get(src), src_mode, False
                    )
                    for dst, dst_port in self.ports.items():
                        for dst_mode in range(dst_port.num_modes):
                            dst_key = f"{dst}@{dst_mode}"
                            coeff = mode_norm[dst][dst_mode] * _get_amps(
                                data[dst], dst_port, self.port_epsilon.get(dst), dst_mode, True
                            )
                            elements[(src_key, dst_key)] = coeff / norm

            for (src_equiv, dst_equiv), (src, dst) in self.element_mappings.items():
                src_num_modes = self.ports[src].num_modes
                dst_num_modes = self.ports[dst].num_modes
                for src_index in range(src_num_modes):
                    for dst_index in range(dst_num_modes):
                        key = (f"{src}@{src_index}", f"{dst}@{dst_index}")
                        equiv_key = (f"{src_equiv}@{src_index}", f"{dst_equiv}@{dst_index}")
                        if key in elements and equiv_key not in elements:
                            elements[equiv_key] = numpy.copy(elements[key])

            # If symmetry was used, calculate and apply mode mapping
            if mode_data.simulation.symmetry != (0, 0, 0):
                data_sym = mode_data
                data_full = {
                    name: self.runners[name].data
                    for name, port in self.ports.items()
                    if not isinstance(port, GaussianPort)
                }
                elements = _mode_remap_from_symmetry(elements, self.ports, data_sym, data_full)

            self._s_matrix = SMatrix(self.frequencies, elements, self.ports)

        return self._s_matrix


def _get_epsilon(
    position: Sequence[float],
    structures: Sequence[tidy3d.Structure],
    background_medium: _Medium,
    frequencies: Sequence[float],
) -> numpy.ndarray:
    for structure in structures[::-1]:
        bb_min, bb_max = structure.geometry.bounds
        if all(
            bb_min[i] <= position[i] <= bb_max[i] for i in range(3)
        ) and structure.geometry.inside(position[0:1], position[1:2], position[2:3]):
            return numpy.array([structure.medium.eps_comp(0, 0, f).real for f in frequencies])
    return numpy.array([background_medium.eps_comp(0, 0, f).real for f in frequencies])


def _grid_shift(source: tidy3d.Source, simulation_grid: tidy3d.Grid) -> tidy3d.Source:
    axis = source.size.index(0)
    center = list(source.center)
    grid_steps = -2 if source.direction == "+" else 2

    grid_boundaries = simulation_grid.boundaries.to_list[axis]
    grid_centers = simulation_grid.centers.to_list[axis]

    before = numpy.argwhere(grid_boundaries < center[axis])
    if len(before) == 0:
        raise RuntimeError(f"Position {center[axis]} is outside of simulation bounds.")

    shifted_index = before.flat[-1] + grid_steps
    if (grid_steps < 0 and shifted_index < 0) or (
        grid_steps > 0 and shifted_index >= len(grid_centers)
    ):
        raise RuntimeError(f"Position {center[axis]} is too close to {'xyz'[axis]} boundary.")

    center[axis] = grid_centers[shifted_index]
    return source.copy(update={"center": center})


def _geometry_key(geom: tidy3d.Geometry) -> tuple[float, float, float, float, str]:
    return tuple(x for corner in geom.bounds for x in corner) + (geom.type,)


def _inner_geometry_sort(geom: tidy3d.Geometry) -> tidy3d.Geometry:
    if isinstance(geom, tidy3d.GeometryGroup):
        return tidy3d.GeometryGroup(
            geometries=sorted([_inner_geometry_sort(g) for g in geom.geometries], key=_geometry_key)
        )
    elif isinstance(geom, tidy3d.ClipOperation):
        return tidy3d.ClipOperation(
            operation=geom.operation,
            geometry_a=_inner_geometry_sort(geom.geometry_a),
            geometry_b=_inner_geometry_sort(geom.geometry_b),
        )
    return geom


class Tidy3DModel(Model):
    """S matrix model based on Tidy3D FDTD calculation.

    Args:
        run_time: Maximal simulation run-time (in seconds).
        medium: Background medium. If ``None``, the technology default is
          used.
        symmetry: Component symmetries.
        boundary_spec: Simulation boundary specifications (absorber by
          default).
        monitors: Extra field monitors added to the simulation.
        structures: Additional structures included in the simulations.
        grid_spec: Simulation grid specification. A single float can be used
          to specify the ``min_steps_per_wvl`` for an auto grid.
        shutoff: Field decay factor for simulation termination.
        subpixel: Flag controlling subpixel averaging in the simulation
          grid.
        courant: Courant stability factor.
        port_symmetries: Port symmetries to reduce the number of simulation
          runs. See note below.
        bounds: Bound overrides for the final simulation.
        verbose: Control solver verbosity.

    If not set, the default grid specification for the component simulations
    is defined based on the wavelengths used in the ``s_matrix`` call.
    Defaults for ``run_time``, ``boundary_spec``, ``shutoff``, ``subpixel``,
    and ``courant`` can be defined in a ``"tidy3d"`` dictionary in
    :attr:`config.default_kwargs`. Note that the values used are the ones
    available at the time of the ``s_matrix`` or ``start`` call, not when
    model is initialized.

    The ``start`` method accepts an ``inputs`` argument as a sequence or set
    of port names to limit the computation to those inputs. Instead of port
    names, ``{port}@{mode}`` specifications are also accepted.

    Note:
        Each item in the ``port_symmetries`` sequence is a tuple
        ``(port1, port2, equivalents)`` indicating that the S matrix
        elements that have ``port2`` as source are equal to those with
        ``port1`` as source with destination ports replaced according to
        ``equivalents``.

        For example, ``('1', '2', {'2':'3', '3':'1'})`` in a 3-port
        component means all Sn2 (2nd column, with port 2 as source) have an
        equivalent in Sm1 (1st column, with port 1 as source), with m:n
        items in the equivalence dictionary, resulting in S22 = S11,
        S32 = S21, S12 = S31 (the equivalence ``'1':'2'`` is automatic). If
        ports are multimode, the symmetry applies to all modes, so
        equivalent port pairs must have the same number of modes.

    See also:
        `Tidy3D Model guide <../guides/Tidy3D_Model.ipynb>`__
    """

    def __init__(
        self,
        run_time: Optional[Union[tidy3d.RunTimeSpec, float]] = None,
        medium: Optional[tidy3d.components.medium.MediumType3D] = None,
        symmetry: Sequence[int] = (0, 0, 0),
        boundary_spec: Optional[tidy3d.BoundarySpec] = None,
        monitors: Sequence[tidy3d.components.monitor.MonitorType] = (),
        structures: Sequence[tidy3d.Structure] = (),
        grid_spec: Union[float, tidy3d.GridSpec] = None,
        shutoff: float = None,
        subpixel: bool = None,
        courant: float = None,
        port_symmetries: Sequence[tuple[str, str, dict[str, str]]] = (),
        bounds: Sequence[Sequence[Optional[float]]] = ((None, None, None), (None, None, None)),
        verbose: bool = True,
    ) -> None:
        super().__init__(
            run_time=run_time,
            medium=medium,
            symmetry=symmetry,
            boundary_spec=boundary_spec,
            monitors=monitors,
            structures=structures,
            grid_spec=grid_spec,
            shutoff=shutoff,
            subpixel=subpixel,
            courant=courant,
            port_symmetries=port_symmetries,
            bounds=bounds,
            verbose=verbose,
        )
        self.run_time = run_time
        self.medium = medium
        self.symmetry = symmetry
        self.boundary_spec = boundary_spec
        self.monitors = monitors
        self.structures = structures
        self.grid_spec = grid_spec
        self.shutoff = shutoff
        self.subpixel = subpixel
        self.courant = courant
        self.bounds = bounds
        self.verbose = verbose
        self.port_symmetries = []
        for src, src_equiv, equiv in port_symmetries:
            eq_copy = dict(equiv)
            eq_copy[src] = src_equiv
            self.port_symmetries.append((src, src_equiv, eq_copy))

    def __copy__(self) -> "Tidy3DModel":
        return Tidy3DModel(
            self.run_time,
            self.medium,
            self.symmetry,
            self.boundary_spec,
            self.monitors,
            self.structures,
            self.grid_spec,
            self.shutoff,
            self.subpixel,
            self.courant,
            self.port_symmetries,
            self.bounds,
            self.verbose,
        )

    def __deepcopy__(self, memo: dict = None) -> "Tidy3DModel":
        return Tidy3DModel(
            self.run_time,
            self.medium,
            libcopy.deepcopy(self.symmetry),
            self.boundary_spec,
            libcopy.deepcopy(self.monitors),
            libcopy.deepcopy(self.structures),
            self.grid_spec,
            self.shutoff,
            self.subpixel,
            self.courant,
            libcopy.deepcopy(self.port_symmetries),
            libcopy.deepcopy(self.bounds),
            self.verbose,
        )

    def __str__(self) -> str:
        return "Tidy3DModel"

    def __repr__(self) -> str:
        return (
            f"Tidy3DModel(run_time={self.run_time!r}, medium={self.medium!r}, "
            f"symmetry={self.symmetry!r}, boundary_spec={self.boundary_spec!r}, "
            f"monitors={self.monitors!r}, structures={self.structures!r}, "
            f"grid_spec={self.grid_spec!r}, shutoff={self.shutoff!r}, "
            f"subpixel={self.subpixel!r}, courant={self.courant!r}, "
            f"port_symmetries={self.port_symmetries!r}, bounds={self.bounds!r}, "
            f"verbose={self.verbose!r})"
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Tidy3DModel) and self.as_bytes == other.as_bytes

    def data_path_for(self, component: Component) -> pathlib.Path:
        """Return the path for the cached data for a component."""
        return _cache_path(_safe_hash(component.name.encode("utf-8")))

    def batch_file_for(self, component: Component) -> pathlib.Path:
        """Return the file used to store the Tidy3D ``BatchData`` for a component."""
        try:
            suffix = _safe_hash(component.as_bytes)
        except Exception:
            suffix = _safe_hash(component.name.encode("utf-8"))
        return self.data_path_for(component) / f"batch_data-{suffix}.json"

    def batch_data_for(self, component: Component) -> Optional[Any]:
        """Return the Tidy3D ``BatchData`` for a given component."""
        batch_file = self.batch_file_for(component)
        if batch_file.is_file():
            from tidy3d.web import BatchData

            return BatchData.from_file(str(batch_file))
        return None

    def _process_port_symmetries(
        self, ports: dict[str, Union[Port, FiberPort, GaussianPort]], component_name: str
    ) -> tuple[set[str], dict[tuple[str, str], tuple[str, str]]]:
        """Return the required simulation sources and mappings for a component."""
        # Ensure consistency if the user changed this outside __init__
        for src, src_equiv, equiv in self.port_symmetries:
            equiv[src] = src_equiv

        required_sources = set(ports.keys())
        element_mappings = {}
        for src, src_equiv, equiv in self.port_symmetries:
            src_port = ports.get(src)
            src_equiv_port = ports.get(src_equiv)
            if src_port is None or src_equiv_port is None:
                missing_port = src if src_port is None else src_equiv
                warnings.warn(
                    f"Port {missing_port} specified in 'port_symmetries' does not exist in "
                    f"component {component_name}."
                )
                continue
            if src_port.num_modes != src_equiv_port.num_modes:
                warnings.warn(
                    f"Port pair {src} and {src_equiv} specified in 'port_symmetries' support "
                    f"different numbers of modes."
                )
                continue

            mapped = {src_equiv}
            element_mappings[(src_equiv, src_equiv)] = (src, src)
            for dst, dst_port in ports.items():
                dst_equiv = equiv.get(dst)
                if dst_equiv is None:
                    continue
                dst_equiv_port = ports.get(dst_equiv)
                if dst_equiv_port is None:
                    warnings.warn(
                        f"Port {dst_equiv} specified in 'port_symmetries' does not exist in "
                        f"component {component_name}."
                    )
                    continue
                if dst_port.num_modes != dst_equiv_port.num_modes:
                    warnings.warn(
                        f"Port pair {dst} and {dst_equiv} specified in 'port_symmetries' support "
                        f"different numbers of modes."
                    )
                    continue
                mapped.add(dst_equiv)
                element_mappings[(src_equiv, dst_equiv)] = (src, dst)

            if len(mapped) == len(ports) and src_equiv in required_sources:
                required_sources.remove(src_equiv)

        return required_sources, element_mappings

    def get_simulations(
        self, component: Component, frequencies: Sequence[float], sources: Sequence[str] = ()
    ) -> Union[dict[str, tidy3d.Simulation], tidy3d.Simulation]:
        """Return all simulations required by this component.

        Args:
            component: Instance of Component for calculation.
            frequencies: Sequence of frequencies for the simulation.
            sources: Port names to be used as sources (``{port}@{mode}``
              specifications are also accepted). If empty, use all required
              sources based on this model's port symmetries.

        Returns:
            Dictionary of ``tidy3d.Simulation`` indexed by source name or
            a single simulation if the component has no ports.
        """
        defaults = config.default_kwargs.get("tidy3d", {})

        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)
        fmin = frequencies.min()
        fmax = frequencies.max()
        fmed = 0.5 * (fmin + fmax)
        max_wavelength = C_0 / fmin
        min_wavelength = C_0 / fmax

        classification = frequency_classification(frequencies)
        medium = (
            component.technology.get_background_medium(classification)
            if self.medium is None
            else self.medium
        )

        grid_spec = (
            self.grid_spec
            if isinstance(self.grid_spec, tidy3d.GridSpec)
            else tidy3d.GridSpec.auto(
                wavelength=min_wavelength,
                min_steps_per_wvl=config.default_mesh_refinement
                if self.grid_spec is None
                else self.grid_spec,
            )
        )

        extrusion_tolerance = 0
        if isinstance(grid_spec.grid_z, tidy3d.AutoGrid):
            grid_lda = min_wavelength if grid_spec.wavelength is None else grid_spec.wavelength
            temp_scene = tidy3d.Scene(
                medium=medium,
                structures=[
                    tidy3d.Structure(
                        geometry=tidy3d.Box(size=(1, 1, 1)), medium=spec.get_medium(classification)
                    )
                    for spec in component.technology.extrusion_specs
                ],
            )
            _, eps_max = temp_scene.eps_bounds(fmed)
            extrusion_tolerance = grid_lda / (grid_spec.grid_z.min_steps_per_wvl * eps_max**0.5)
        elif isinstance(grid_spec.grid_z, tidy3d.UniformGrid):
            extrusion_tolerance = grid_spec.grid_z.dl
        elif isinstance(grid_spec.grid_z, tidy3d.CustomGrid) and len(grid_spec.grid_z.dl) > 0:
            extrusion_tolerance = min(grid_spec.grid_z.dl)

        boundary_spec = (
            defaults.get(
                "boundary_spec",
                tidy3d.BoundarySpec.all_sides(boundary=tidy3d.Absorber(num_layers=70)),
            )
            if self.boundary_spec is None
            else self.boundary_spec
        )

        (xmin, ymin), (xmax, ymax) = component.bounds()
        structures = [
            struct.to_tidy3d()
            for struct in component.extrude(
                0.5 * max_wavelength + max(xmax - xmin, ymax - ymin),
                extrusion_tolerance=extrusion_tolerance,
                classification=classification,
            )
        ]

        # Sort to improve caching, but don't reorder different media
        i = 0
        while i < len(structures):
            current_medium = structures[i].medium
            j = i + 1
            while j < len(structures) and structures[j].medium == current_medium:
                j += 1
            # Even if j == i + 1 we want to sort internal geometries
            structures[i:j] = (
                tidy3d.Structure(geometry=geometry, medium=current_medium)
                for geometry in sorted(
                    [_inner_geometry_sort(s.geometry) for s in structures[i:j]], key=_geometry_key
                )
            )
            i = j

        component_ports = component.select_ports(classification)
        port_structures = [
            structure
            for _, port in sorted(component_ports.items())
            if isinstance(port, FiberPort)
            for structure in port.to_tidy3d_structures()
        ]
        all_structures = structures + port_structures + list(self.structures)

        if len(sources) == 0:
            sources, _ = self._process_port_symmetries(component_ports, component.name)

        port_monitors = []
        port_sources = {}
        unused_sources = []
        for name, port in component_ports.items():
            if isinstance(port, (Port, FiberPort)):
                monitor = port.to_tidy3d_monitor(frequencies, name=name)
                unused = True
                for mode_index in range(port.num_modes):
                    port_mode = f"{name}@{mode_index}"
                    if name in sources or port_mode in sources:
                        unused = False
                        port_sources[port_mode] = port.to_tidy3d_source(
                            frequencies, mode_index=mode_index, name=name
                        )
                if unused:
                    unused_sources.append(
                        port.to_tidy3d_source(frequencies, mode_index=0, name=name)
                    )

            else:
                epsilon_r = _get_epsilon(port.center, all_structures, medium, frequencies)
                monitor = port.to_tidy3d_monitor(frequencies, medium=epsilon_r, name=name)
                port_mode = f"{name}@0"
                if name in sources or port_mode in sources:
                    port_sources[port_mode] = port.to_tidy3d_source(
                        frequencies, medium=epsilon_r, name=name
                    )
                else:
                    unused_sources.append(
                        port.to_tidy3d_source(frequencies, medium=epsilon_r, name=name)
                    )

            port_monitors.append(monitor)

        # Simulation bounds
        zmin = 1e30
        zmax = -1e30
        for monitor in port_monitors:
            xmin = min(xmin, monitor.bounds[0][0])
            ymin = min(ymin, monitor.bounds[0][1])
            zmin = min(zmin, monitor.bounds[0][2])
            xmax = max(xmax, monitor.bounds[1][0])
            ymax = max(ymax, monitor.bounds[1][1])
            zmax = max(zmax, monitor.bounds[1][2])
        for s in structures:
            for i in range(2):
                lim = s.geometry.bounds[i][2]
                if -Z_MAX <= lim <= Z_MAX:
                    zmin = min(zmin, lim)
                    zmax = max(zmax, lim)
        if zmin > zmax:
            raise RuntimeError("No valid extrusion elements present in the component.")

        pml_gap = 0.6 * max_wavelength
        if isinstance(boundary_spec.x.minus, (tidy3d.PML, tidy3d.StablePML)):
            xmin -= pml_gap
        if isinstance(boundary_spec.x.plus, (tidy3d.PML, tidy3d.StablePML)):
            xmax += pml_gap
        if isinstance(boundary_spec.y.minus, (tidy3d.PML, tidy3d.StablePML)):
            ymin -= pml_gap
        if isinstance(boundary_spec.y.plus, (tidy3d.PML, tidy3d.StablePML)):
            ymax += pml_gap
        if isinstance(boundary_spec.z.minus, (tidy3d.PML, tidy3d.StablePML)):
            zmin -= pml_gap
        if isinstance(boundary_spec.z.plus, (tidy3d.PML, tidy3d.StablePML)):
            zmax += pml_gap

        bounds = numpy.array(((xmin, ymin, zmin), (xmax, ymax, zmax)))

        center = tuple(snap_to_grid(v) / 2 for v in bounds[0] + bounds[1])

        # Include margin for port sources
        size = tuple(snap_to_grid(v + max_wavelength) for v in bounds[1] - bounds[0])

        bounding_box = tidy3d.Box(center=center, size=size)

        shutoff = defaults.get("shutoff", 1.0e-5) if self.shutoff is None else self.shutoff
        subpixel = defaults.get("subpixel", True) if self.subpixel is None else self.subpixel
        courant = defaults.get("courant", 0.99) if self.courant is None else self.courant

        base_simulation = tidy3d.Simulation(
            center=center,
            size=size,
            run_time=1e-12 if self.run_time is None else self.run_time,
            medium=medium,
            symmetry=(0, 0, 0),
            structures=[s for s in all_structures if bounding_box.intersects(s.geometry)],
            boundary_spec=boundary_spec,
            monitors=list(self.monitors) + port_monitors,
            grid_spec=grid_spec,
            shutoff=shutoff,
            subpixel=subpixel,
            courant=courant,
        )

        # Update keywords from base simulation
        update = {"symmetry": self.symmetry}

        if len(port_sources) == 0:
            return base_simulation.copy(update=update)

        # RunTimeSpec can only be used when sources are defined
        if self.run_time is None:
            update["run_time"] = defaults.get(
                "run_time", tidy3d.RunTimeSpec(quality_factor=5.0, source_factor=3.0)
            )

        # Use base grid to shift sources and update base simulation
        grid = base_simulation.grid

        delta_factor = 3

        for name in port_sources:
            source = _grid_shift(port_sources[name], grid)
            port_sources[name] = source

            delta = delta_factor * (xmin - source.bounds[0][0])
            if delta > 0:
                xmin -= delta
            delta = delta_factor * (source.bounds[1][0] - xmax)
            if delta > 0:
                xmax += delta

            delta = delta_factor * (ymin - source.bounds[0][1])
            if delta > 0:
                ymin -= delta
            delta = delta_factor * (source.bounds[1][1] - ymax)
            if delta > 0:
                ymax += delta

            delta = delta_factor * (zmin - source.bounds[0][2])
            if delta > 0:
                zmin -= delta
            delta = delta_factor * (source.bounds[1][2] - zmax)
            if delta > 0:
                zmax += delta

        for unused_source in unused_sources:
            source = _grid_shift(unused_source, grid)

            delta = delta_factor * (xmin - source.bounds[0][0])
            if delta > 0:
                xmin -= delta
            delta = delta_factor * (source.bounds[1][0] - xmax)
            if delta > 0:
                xmax += delta

            delta = delta_factor * (ymin - source.bounds[0][1])
            if delta > 0:
                ymin -= delta
            delta = delta_factor * (source.bounds[1][1] - ymax)
            if delta > 0:
                ymax += delta

            delta = delta_factor * (zmin - source.bounds[0][2])
            if delta > 0:
                zmin -= delta
            delta = delta_factor * (source.bounds[1][2] - zmax)
            if delta > 0:
                zmax += delta

        for monitor in port_monitors:
            if xmin >= monitor.bounds[0][0]:
                xmin -= config.grid
            if ymin >= monitor.bounds[0][1]:
                ymin -= config.grid
            if zmin >= monitor.bounds[0][2]:
                zmin -= config.grid
            if xmax <= monitor.bounds[1][0]:
                xmax += config.grid
            if ymax <= monitor.bounds[1][1]:
                ymax += config.grid
            if zmax <= monitor.bounds[1][2]:
                zmax += config.grid

        bounds = numpy.array(((xmin, ymin, zmin), (xmax, ymax, zmax)))

        # Bounds override
        for i in range(3):
            if self.bounds[0][i] is not None:
                bounds[0, i] = self.bounds[0][i]
            if self.bounds[1][i] is not None:
                bounds[1, i] = self.bounds[1][i]

        update["center"] = tuple(snap_to_grid(v) / 2 for v in bounds[0] + bounds[1])
        update["size"] = tuple(snap_to_grid(v) for v in bounds[1] - bounds[0])

        bounding_box = tidy3d.Box(center=update["center"], size=update["size"])

        update["structures"] = [s for s in all_structures if bounding_box.intersects(s.geometry)]

        if self.boundary_spec is None and any(s == 0 for s in size):
            axis = "yxz"[size.index(0)]
            update["boundary_spec"] = boundary_spec.copy(
                update={axis: tidy3d.Boundary(minus=tidy3d.Periodic(), plus=tidy3d.Periodic())}
            )

        # Only the first simulation will store mode field data
        simulations = {}
        first = True
        for name in sorted(port_sources):
            update["sources"] = [port_sources[name]]
            simulations[name] = base_simulation.copy(update=update)
            if first:
                first = False
                update["monitors"] = list(self.monitors) + [
                    mon.copy(update={"store_fields_direction": None})
                    if isinstance(mon, tidy3d.ModeMonitor)
                    else mon
                    for mon in port_monitors
                ]

        return simulations

    @cache_s_matrix
    def start(
        self,
        component: Component,
        frequencies: Sequence[float],
        *,
        inputs: Sequence[str] = (),
        verbose: Optional[bool] = None,
        **kwargs,
    ) -> _Tidy3DModelRunner:
        """Start computing the S matrix response from a component.

        Args:
            component: Component from which to compute the S matrix.
            frequencies: Sequence of frequencies at which to perform the
              computation.
            inputs: Limit calculation to specific inputs. Each item must be
              a port name or a ``{port}@{mode}`` specification.
            verbose: If set, overrides the model's `verbose` attribute.
            **kwargs: Unused.

        Returns:
            Result object with attributes ``status`` and ``s_matrix``.

        Important:
            When using geometry symmetry, the mode numbering in ``inputs``
            is relative to the solver run *with the symmetry applied*, not
            the mode number presented in the final S matrix.
        """
        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)
        classification = frequency_classification(frequencies)
        inputs = tuple(inputs)
        component_ports = component.select_ports(classification)
        if verbose is None:
            verbose = self.verbose

        required_sources, element_mappings = self._process_port_symmetries(
            component_ports, component.name
        )
        if len(inputs) > 0:
            required_sources = inputs

        simulations = self.get_simulations(component, frequencies, required_sources)

        sim = next(iter(simulations.values()))
        port_epsilon = {
            name: _get_epsilon(port.center, sim.structures, sim.medium, frequencies)
            for name, port in component_ports.items()
            if not isinstance(port, Port)
        }

        folder_name = _filename_cleanup(component.name)
        if len(folder_name) == 0:
            folder_name = "default"

        return _Tidy3DModelRunner(
            frequencies=frequencies,
            simulations=simulations,
            ports=component_ports,
            port_epsilon=port_epsilon,
            element_mappings=element_mappings,
            folder_name=folder_name,
            data_path=self.data_path_for(component),
            batch_file=self.batch_file_for(component),
            verbose=verbose,
        )

    @property
    def as_bytes(self) -> bytes:
        """Serialize this model."""
        obj = {
            "symmetry": self.symmetry,
            "shutoff": self.shutoff,
            "subpixel": self.subpixel,
            "courant": self.courant,
            "bounds": self.bounds,
            "verbose": self.verbose,
        }

        if self.run_time is not None:
            obj["run_time"] = (
                self.run_time.dict()
                if isinstance(self.run_time, tidy3d.components.base.Tidy3dBaseModel)
                else self.run_time
            )
        if self.medium is not None:
            obj["medium"] = json.loads(self.medium.json())
        if self.boundary_spec is not None:
            obj["boundary_spec"] = self.boundary_spec.dict()
        if len(self.monitors) > 0:
            obj["monitors"] = [m.dict() for m in self.monitors]
        if len(self.structures) > 0:
            obj["structures"] = [_convert_arrays(s.dict()) for s in self.structures]
        if self.grid_spec is not None:
            obj["grid_spec"] = (
                self.grid_spec.dict()
                if isinstance(self.grid_spec, tidy3d.GridSpec)
                else self.grid_spec
            )
        if len(self.port_symmetries) > 0:
            obj["port_symmetries"] = self.port_symmetries

        # Note: keys are sorted to guarantee the representation is consistent for caching
        return zlib.compress(json.dumps(obj, sort_keys=True).encode("utf-8"))

    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "Tidy3DModel":
        """De-serialize this model."""
        obj = json.loads(zlib.decompress(byte_repr).decode("utf-8"))

        for field, field_type in [
            ("medium", tidy3d.components.medium.MediumType3D),
            ("boundary_spec", tidy3d.BoundarySpec),
        ]:
            if obj.get(field, None) is not None:
                obj[field] = pydantic.v1.parse_obj_as(
                    field_type, obj[field], type_name=obj[field]["type"]
                )

        if isinstance(obj.get("run_time", None), dict):
            obj["run_time"] = pydantic.v1.parse_obj_as(
                tidy3d.RunTimeSpec,
                obj["run_time"],
                type_name=obj["run_time"]["type"],
            )

        if isinstance(obj.get("grid_spec", None), dict):
            obj["grid_spec"] = pydantic.v1.parse_obj_as(
                tidy3d.GridSpec,
                obj["grid_spec"],
                type_name=obj["grid_spec"]["type"],
            )

        obj["monitors"] = [
            pydantic.v1.parse_obj_as(
                tidy3d.components.monitor.MonitorType, mon, type_name=mon["type"]
            )
            for mon in obj.get("monitors", ())
        ]

        obj["structures"] = [
            pydantic.v1.parse_obj_as(tidy3d.Structure, s, type_name=s["type"])
            for s in obj.get("structures", ())
        ]

        return cls(**obj)


def test_port_symmetries(component: Component, frequencies: Sequence[float], verbose=True) -> bool:
    success = True
    for name, model in component.models.items():
        if isinstance(model, Tidy3DModel):
            if len(model.port_symmetries) == 0:
                continue
            if verbose:
                print(f"Testing {name} for {model.port_symmetries}")
            m = model.__deepcopy__()
            m.verbose = False
            s0 = m.s_matrix(component, frequencies)
            m.port_symmetries = []
            s1 = m.s_matrix(component, frequencies)
            ax = None
            for k in s0.elements:
                if not numpy.allclose(s0[k], s1[k], atol=0.02):
                    success = False
                    if ax is None:
                        try:
                            from matplotlib import pyplot

                            _, ax = pyplot.subplots(2, 2, figsize=(10, 6), tight_layout=True)
                        except ImportError:
                            pass
                    if ax is not None:
                        ax[0, 0].plot(frequencies, numpy.real(s0[k]), label=str(k) + " (sym)")
                        ax[0, 1].plot(frequencies, numpy.imag(s0[k]), label=str(k) + " (sym)")
                        ax[1, 0].plot(frequencies, numpy.real(s1[k]), label=str(k))
                        ax[1, 1].plot(frequencies, numpy.imag(s1[k]), label=str(k))
                    if verbose:
                        print(f"Error in {k}")
            if ax is not None:
                ax[0, 0].set(xlabel="Frequency (Hz)", ylabel="Real part")
                ax[0, 1].set(xlabel="Frequency (Hz)", ylabel="Imaginary part")
                ax[1, 0].set(xlabel="Frequency (Hz)", ylabel="Real part")
                ax[1, 1].set(xlabel="Frequency (Hz)", ylabel="Imaginary part")
                for a in ax.flat:
                    a.legend()
    if success and verbose:
        print("SUCCESS")
    return success


register_model_class(Tidy3DModel)
