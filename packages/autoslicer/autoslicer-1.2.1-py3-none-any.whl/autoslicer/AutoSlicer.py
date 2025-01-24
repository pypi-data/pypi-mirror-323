import os
import SimpleITK as sitk
import nibabel as nib
import numpy as np
import torch
from totalsegmentator.python_api import totalsegmentator
from totalsegmentator.nifti_ext_header import load_multilabel_nifti
import matplotlib.pyplot as plt
import vtk
import vtk.util.numpy_support as numpy_support

# Density map for each label (modifiable according to requirements)
DENSITY_MAP = {
    1: 1.05, 2: 1.06, 3: 1.06, 4: 1.02, 5: 1.05, 6: 1.04, 7: 1.04, 8: 1.04, 9: 1.04,
    10: 0.3, 11: 0.3, 12: 0.3, 13: 0.3, 14: 0.3, 15: 1.04, 16: 0.8, 17: 1.04, 18: 1.04,
    19: 1.04, 20: 1.04, 21: 1.05, 22: 1.04, 23: 1.01, 24: 1.01, 25: 1.9, 26: 1.9,
    27: 1.9, 28: 1.9, 29: 1.9, 30: 1.9, 31: 1.9, 32: 1.9, 33: 1.9, 34: 1.9, 35: 1.9,
    36: 1.9, 37: 1.9, 38: 1.9, 39: 1.9, 40: 1.9, 41: 1.9, 42: 1.9, 43: 1.9, 44: 1.9,
    45: 1.9, 46: 1.9, 47: 1.9, 48: 1.9, 49: 1.9, 50: 1.9, 51: 1.06, 52: 1.05, 53: 1.05,
    54: 1.05, 55: 1.05, 56: 1.05, 57: 1.05, 58: 1.05, 59: 1.05, 60: 1.05, 61: 1.06,
    62: 1.05, 63: 1.05, 64: 1.05, 65: 1.05, 66: 1.05, 67: 1.05, 68: 1.05, 69: 1.85,
    70: 1.85, 71: 1.85, 72: 1.85, 73: 1.85, 74: 1.85, 75: 1.85, 76: 1.85, 77: 1.85,
    78: 1.85, 79: 1.04, 80: 1.06, 81: 1.06, 82: 1.06, 83: 1.06, 84: 1.06, 85: 1.06,
    86: 1.06, 87: 1.06, 88: 1.06, 89: 1.06, 90: 1.04, 91: 1.9, 92: 1.85, 93: 1.85,
    94: 1.85, 95: 1.85, 96: 1.85, 97: 1.85, 98: 1.85, 99: 1.1, 100: 1.1, 101: 1.85,
    102: 1.85, 103: 1.85, 104: 1.85, 105: 1.85, 106: 1.85, 107: 1.85, 108: 1.85,
    109: 1.85, 110: 1.85, 111: 1.85, 112: 1.85, 113: 1.85, 114: 1.85, 115: 1.85,
    116: 1.85, 117: 1.8, 118: 2
}

class AutoSlicer:
    """
    AutoSlicer performs:
      1. DICOM to NIfTI conversion
      2. TotalSegmentator-based segmentation
      3. Adding a skin label in a given intensity range
      4. Computing mass, volume, inertia, center of mass
      5. Generating a VTK model file
      6. Visualizing the VTK (optional)
    """

    def __init__(self, workspace: str):
        """
        Initializes AutoSlicer with file paths and threshold defaults.

        Args:
            workspace (str): Name of the workspace directory.
        """
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace = os.path.join(self.current_dir, workspace)
        self._ensure_directory(self.workspace)

        # Default intensity thresholds
        self.lower_ = -96.25
        self.upper_ = 153.46

        # File path configuration
        self.source_volume_path = os.path.join(self.workspace, "CT_Source_Volume.nii.gz")
        self.total_seg_result = os.path.join(self.workspace, "CT_TotalSegmentation.nii.gz")
        self.other_soft_tissue = os.path.join(self.workspace, "CT_SoftTissueLabel0.nii.gz")
        self.final_seg_result = os.path.join(self.workspace, "CT_SoftTissueLabel1.nii.gz")
        self.vtk_path = os.path.join(self.workspace, "CT_visualization.vtk")

        # The screenshot will be saved here
        self.output_image = os.path.join(self.workspace, "vtk_visualization.png")

    @staticmethod
    def _ensure_directory(path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def set_density(self, label: int, value: float) -> None:
        if label in DENSITY_MAP:
            DENSITY_MAP[label] = value
        else:
            print(f"Label {label} not found in the density map. Skipping.")

    def set_threshold(self, lower_val: float, upper_val: float) -> None:
        self.lower_ = lower_val
        self.upper_ = upper_val

    # ----------------- NIfTI Creation ----------------- #
    @staticmethod
    def _get_voxel_size(input_folder: str):
        try:
            reader = sitk.ImageSeriesReader()
            dicom_series = reader.GetGDCMSeriesIDs(input_folder)
            if not dicom_series:
                raise ValueError("No DICOM series found.")

            series_file_names = reader.GetGDCMSeriesFileNames(input_folder, dicom_series[0])
            reader.SetFileNames(series_file_names)
            image = reader.Execute()

            voxel_size = image.GetSpacing()
            print(f"Voxel size (x, y, z): {voxel_size}")
            unit = "mm"
            print(f"Assumed unit: {unit}")
            return voxel_size, unit

        except Exception as e:
            print(f"Error reading voxel size: {e}")
            return None, None

    def _dicom_to_nifti(self, input_folder: str, output_path: str) -> None:
        try:
            reader = sitk.ImageSeriesReader()
            self._get_voxel_size(input_folder)

            dicom_series = reader.GetGDCMSeriesIDs(input_folder)
            if not dicom_series:
                raise ValueError("No DICOM series found.")

            print(f"Found {len(dicom_series)} DICOM series.")
            for series_id in dicom_series:
                series_file_names = reader.GetGDCMSeriesFileNames(input_folder, series_id)
                reader.SetFileNames(series_file_names)
                image = reader.Execute()
                sitk.WriteImage(image, output_path)
                print(f"Converted series {series_id} to {output_path}")

            print("All DICOM series converted successfully.")

        except Exception as e:
            print(f"Error during DICOM->NIfTI: {e}")

    def create_nifti(self, input_folder: str) -> None:
        self._dicom_to_nifti(input_folder, self.source_volume_path)

    # ----------------- Segmentation ----------------- #
    def _segment_image(self, input_image_path: str, output_path: str) -> None:
        device = "gpu" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        try:
            input_img = nib.load(input_image_path)
            print("Running TotalSegmentator...")
            output_img = totalsegmentator(
                input=input_img,
                task="total",
                ml=True,
                device=device
            )
            nib.save(output_img, output_path)
            print(f"Segmentation done. Saved to: {output_path}")
        except Exception as e:
            print(f"Error in segmentation: {e}")
            raise

    def _label_segmentation(self, seg_result_path: str, labeled_output_path: str) -> None:
        try:
            print("Loading segmentation with labels...")
            seg_nifti_img, label_map_dict = load_multilabel_nifti(seg_result_path)

            label_img = seg_nifti_img.get_fdata().astype(int)
            label_nifti = nib.Nifti1Image(label_img, seg_nifti_img.affine, seg_nifti_img.header)
            label_nifti.header["descrip"] = "Label Map for 3D Slicer"

            for label, description in label_map_dict.items():
                label_nifti.header.extensions.append(
                    nib.nifti1.Nifti1Extension(4, f"{label}: {description}".encode("utf-8"))
                )

            nib.save(label_nifti, labeled_output_path)
            print(f"Labeled segmentation saved to: {labeled_output_path}")
        except Exception as e:
            print(f"Error labeling segmentation: {e}")
            raise

    def create_segmentation(self) -> None:
        self._segment_image(self.source_volume_path, self.total_seg_result)
        self._label_segmentation(self.total_seg_result, self.other_soft_tissue)

    # ----------------- Skin Labeling ----------------- #
    @staticmethod
    def _load_nifti_file(file_path: str):
        nifti_img = nib.load(file_path)
        return nifti_img.get_fdata(), nifti_img.affine

    @staticmethod
    def _save_nifti_file(data: np.ndarray, affine: np.ndarray, file_path: str) -> None:
        new_nifti_img = nib.Nifti1Image(data, affine)
        nib.save(new_nifti_img, file_path)

    def _add_skin_label(self, src_volume: np.ndarray, seg_result: np.ndarray) -> np.ndarray:
        """
        Use self.lower_ and self.upper_ to define the intensity range for 'skin',
        then label it as 118 in the final segmentation array.
        """
        skin_candidate = (src_volume >= self.lower_) & (src_volume <= self.upper_)
        unlabeled_area = (seg_result == 0)
        skin_label_area = skin_candidate & unlabeled_area

        updated_seg = seg_result.copy()
        updated_seg[skin_label_area] = 118
        return updated_seg

    def create_soft_tissue_segmentation(self) -> None:
        seg_result, seg_affine = self._load_nifti_file(self.other_soft_tissue)
        source_volume, _ = self._load_nifti_file(self.source_volume_path)

        updated_seg = self._add_skin_label(source_volume, seg_result)
        self._save_nifti_file(updated_seg, seg_affine, self.final_seg_result)
        print(f"Updated segmentation saved: {self.final_seg_result}")

    # ----------------- Inertia + Center of Mass ----------------- #
    @staticmethod
    def _get_segmentation_labels(seg_file: str) -> list:
        nifti_img = nib.load(seg_file)
        seg_data = nifti_img.get_fdata()
        unique_labels = np.unique(seg_data)
        return [int(x) for x in unique_labels.tolist()]

    def _calculate_inertia_parameters(self, seg_file: str) -> dict:
        """
        Calculates volume, mass, inertia, and center of mass across all labeled structures.
        NOTE: For an actual medical scenario, replace (1,1,1) with real voxel spacing if known.
        """
        voxel_size = (1, 1, 1)  # Modify if you know the real spacing
        labels = self._get_segmentation_labels(seg_file)
        nifti_img = nib.load(seg_file)
        seg_data = nifti_img.get_fdata()

        # Convert 1 mm^3 to 0.001 cm^3
        voxel_vol_cm3 = (voxel_size[0] * voxel_size[1] * voxel_size[2]) / 1000.0

        total_mass = 0.0
        total_volume = 0.0
        total_inertia_tensor = np.zeros((3, 3))

        acc_mass_times_centroid = np.zeros(3)
        acc_mass = 0.0

        for label in labels:
            if label == 0:
                continue
            if label not in DENSITY_MAP:
                print(f"Warning: Label {label} not in density map. Skipping.")
                continue

            mask = (seg_data == label)
            num_voxels = mask.sum()
            if num_voxels == 0:
                continue

            density = DENSITY_MAP[label]
            volume = num_voxels * voxel_vol_cm3
            mass = (volume * density) / 1000.0  # convert volume from cm^3 to L, then multiply by density

            coords = np.array(np.where(mask)).T
            coords_mm = coords * voxel_size
            centroid = coords_mm.mean(axis=0)

            acc_mass_times_centroid += mass * centroid
            acc_mass += mass

            # For inertia, each voxel is the same mass = mass / num_voxels
            inertia_tensor = np.zeros((3, 3))
            for c in coords_mm:
                rel_pos = c - centroid
                x, y, z = rel_pos
                # Basic inertia formula
                inertia_tensor += np.array([
                    [y**2 + z**2, -x*y,       -x*z],
                    [-x*y,        x**2 + z**2, -y*z],
                    [-x*z,        -y*z,       x**2 + y**2]
                ]) * mass / num_voxels

            total_volume += volume
            total_mass += mass
            total_inertia_tensor += inertia_tensor

        if acc_mass > 0:
            global_com = acc_mass_times_centroid / acc_mass
        else:
            global_com = np.zeros(3)

        result = {
            "T1": {"name": "Volume", "value": total_volume, "unit": "cm³"},
            "T2": {"name": "Mass",   "value": total_mass,   "unit": "kg"},
            "T3": {"name": "Total Inertia Tensor", "value": total_inertia_tensor, "unit": "kg·mm²"},
            "T4": {"name": "Center of Mass",       "value": global_com.tolist(),  "unit": "mm"}
        }
        return result

    def get_VTK_file(self):
        """
        Generates a VTK file from the final segmentation, with a 'Density' array
        stored per label as a point data array in the polygon mesh.
        """
        seg_file = self.final_seg_result
        output_file_name = self.vtk_path

        seg_reader = vtk.vtkNIFTIImageReader()
        seg_reader.SetFileName(seg_file)
        seg_reader.Update()
        seg_image = seg_reader.GetOutput()

        seg_array = numpy_support.vtk_to_numpy(seg_image.GetPointData().GetScalars())
        unique_labels = np.unique(seg_array)

        density_lut = {}
        for label in unique_labels:
            if label == 0:
                continue
            density_lut[label] = DENSITY_MAP.get(int(label), 1.0)

        append_filter = vtk.vtkAppendPolyData()

        for label in unique_labels:
            if label == 0:
                continue

            thresh = vtk.vtkImageThreshold()
            thresh.SetInputData(seg_image)
            thresh.ThresholdBetween(label, label)
            thresh.SetInValue(1)
            thresh.SetOutValue(0)
            thresh.Update()

            cast_filter = vtk.vtkImageCast()
            cast_filter.SetInputConnection(thresh.GetOutputPort())
            cast_filter.SetOutputScalarTypeToUnsignedChar()
            cast_filter.Update()

            contour = vtk.vtkMarchingCubes()
            contour.SetInputConnection(cast_filter.GetOutputPort())
            contour.SetValue(0, 0.5)
            contour.Update()

            smooth = vtk.vtkSmoothPolyDataFilter()
            smooth.SetInputConnection(contour.GetOutputPort())
            smooth.SetNumberOfIterations(30)
            smooth.SetRelaxationFactor(0.1)
            smooth.FeatureEdgeSmoothingOff()
            smooth.BoundarySmoothingOn()
            smooth.Update()

            fill_holes = vtk.vtkFillHolesFilter()
            fill_holes.SetInputConnection(smooth.GetOutputPort())
            fill_holes.SetHoleSize(1000.0)
            fill_holes.Update()

            polydata = fill_holes.GetOutput()
            density = density_lut[label]

            density_array = vtk.vtkFloatArray()
            density_array.SetName("Density")
            density_array.SetNumberOfComponents(1)
            density_array.SetNumberOfTuples(polydata.GetNumberOfPoints())
            density_array.FillComponent(0, density)
            polydata.GetPointData().AddArray(density_array)

            append_filter.AddInputData(polydata)

        append_filter.Update()

        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(append_filter.GetOutputPort())
        cleaner.Update()

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(output_file_name)
        writer.SetInputConnection(cleaner.GetOutputPort())
        writer.Write()

    def calculate_inertia(self) -> dict:
        return self._calculate_inertia_parameters(self.final_seg_result)

    def run_automation(self, input_folder: str) -> dict:
        """
        One-click process:
          1. Convert DICOM -> NIfTI
          2. Perform segmentation
          3. Add skin label
          4. Compute inertia/center of mass
          5. Generate VTK file

        Returns a dict of computed volume, mass, inertia, and center of mass.
        """
        self.create_nifti(input_folder)
        self.create_segmentation()
        self.create_soft_tissue_segmentation()
        self.get_VTK_file()
        result = self.calculate_inertia()

        # Cleanup temporary files if desired
        try:
            if os.path.exists(self.other_soft_tissue):
                os.remove(self.other_soft_tissue)
                print(f"Deleted temp file: {self.other_soft_tissue}")
            if os.path.exists(self.total_seg_result):
                os.remove(self.total_seg_result)
                print(f"Deleted temp file: {self.total_seg_result}")
        except Exception as e:
            print(f"Error deleting temp files: {e}")

        return result

    # ---------------- Visualization Method (Optional) ----------------
    def visualize_with_coordinate_axes(self, original_com=None, decimate_ratio=0.0):
        """
        Reads the self.vtk_path VTK model and visualizes it with:
          1) Model aligned so that the bounding box min corner is at (0,0,0)
          2) vtkCubeAxesActor for annotated axes
          3) If original_com is provided, displays a sphere at the center of mass
             (plus lines projecting to x=0, y=0, and z=0)
          4) decimate_ratio can reduce the polygon count to speed up rendering
          5) A screenshot is saved to self.output_image, capturing the entire model
        """
        if not os.path.exists(self.vtk_path):
            print(f"VTK file not found: {self.vtk_path}")
            return

        # ----------------- Read the VTK mesh ----------------- #
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(self.vtk_path)
        reader.Update()
        polydata = reader.GetOutput()

        # ----------------- Optional decimation ----------------- #
        if decimate_ratio > 0:
            polydata = self._decimate_polydata(polydata, decimate_ratio)

        # ----------------- Translate geometry to origin ----------------- #
        transformed_polydata, dx, dy, dz, transform = self._transform_to_origin(polydata)

        # ----------------- Create actor from polydata ----------------- #
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(transformed_polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(0.2)  # Make main actor partially transparent

        # ----------------- Create renderer, add actor ----------------- #
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.1)  # dark background

        # ----------------- Add Cube Axes ----------------- #
        cube_axes = vtk.vtkCubeAxesActor()
        cube_axes.SetBounds(0, dx, 0, dy, 0, dz)
        cube_axes.SetCamera(renderer.GetActiveCamera())
        cube_axes.SetXTitle("X Axis (mm)")
        cube_axes.SetYTitle("Y Axis (mm)")
        cube_axes.SetZTitle("Z Axis (mm)")
        # Some VTK versions might require .SetFlyModeToStatic() or .SetFlyModeToStaticEdges()
        cube_axes.SetFlyModeToStaticEdges()
        for i in range(3):
            cube_axes.GetTitleTextProperty(i).SetColor(1, 1, 1)
            cube_axes.GetLabelTextProperty(i).SetColor(1, 1, 1)
        renderer.AddActor(cube_axes)

        # ----------------- Optionally add COM sphere + lines ----------------- #
        if original_com is not None:
            tx, ty, tz = transform.GetPosition()
            cx_new = original_com[0] + tx
            cy_new = original_com[1] + ty
            cz_new = original_com[2] + tz

            # 1) Create a bigger, brighter sphere at COM
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(cx_new, cy_new, cz_new)
            sphere_source.SetRadius(10.0)  # e.g., 10.0 mm radius
            sphere_source.Update()

            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())
            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)
            sphere_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # bright red
            renderer.AddActor(sphere_actor)

            # 2) Create lines from COM to the bounding planes
            line_com_x = self._create_line_actor(
                (cx_new, cy_new, cz_new),
                (0, cy_new, cz_new),
                color=(0.0, 1.0, 0.0),  # bright green
                width=3.0
            )
            line_com_y = self._create_line_actor(
                (cx_new, cy_new, cz_new),
                (cx_new, 0, cz_new),
                color=(0.0, 1.0, 0.0),
                width=3.0
            )
            line_com_z = self._create_line_actor(
                (cx_new, cy_new, cz_new),
                (cx_new, cy_new, 0),
                color=(0.0, 1.0, 0.0),
                width=3.0
            )
            renderer.AddActor(line_com_x)
            renderer.AddActor(line_com_y)
            renderer.AddActor(line_com_z)

            # 3) Add text overlay for COM
            text_actor = vtk.vtkTextActor()
            text_info = (
                f"Original COM: ({original_com[0]:.2f}, {original_com[1]:.2f}, {original_com[2]:.2f})\n"
                f"New COM: ({cx_new:.2f}, {cy_new:.2f}, {cz_new:.2f})"
            )
            text_actor.SetInput(text_info)
            text_actor.GetTextProperty().SetFontSize(18)
            text_actor.GetTextProperty().SetColor(1, 1, 1)
            text_actor.SetDisplayPosition(10, 10)
            renderer.AddActor2D(text_actor)

        # ----------------- Create a window + interactor ----------------- #
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(1024, 768)  # Larger window for a bigger screenshot
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # ----------------- Ensure entire model is in view ----------------- #
        renderer.ResetCamera()

        # ----------------- Render the scene first ----------------- #
        render_window.Render()

        # ----------------- Take a screenshot ----------------- #
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(render_window)
        window_to_image_filter.Update()

        png_writer = vtk.vtkPNGWriter()
        png_writer.SetFileName(self.output_image)
        png_writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        png_writer.Write()
        print(f"Screenshot saved to: {self.output_image}")

        # ----------------- Start interactive window ----------------- #
        print("VTK window started. Press 'q' or close the window to exit.")
        interactor.Start()

    # Helper methods for visualization
    def _decimate_polydata(self, polydata, reduction=0.3):
        decimator = vtk.vtkDecimatePro()
        decimator.SetInputData(polydata)
        decimator.SetTargetReduction(reduction)
        decimator.PreserveTopologyOn()
        decimator.Update()
        return decimator.GetOutput()

    def _transform_to_origin(self, polydata):
        bounds = polydata.GetBounds()  # (xmin, xmax, ymin, ymax, zmin, zmax)
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        dx = xmax - xmin
        dy = ymax - ymin
        dz = zmax - zmin

        transform = vtk.vtkTransform()
        transform.Translate(-xmin, -ymin, -zmin)

        tf_filter = vtk.vtkTransformPolyDataFilter()
        tf_filter.SetInputData(polydata)
        tf_filter.SetTransform(transform)
        tf_filter.Update()

        return tf_filter.GetOutput(), dx, dy, dz, transform

    def _create_line_actor(self, pt1, pt2, color=(0.7, 0.7, 0.7), width=2.0):
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(pt1)
        line_source.SetPoint2(pt2)
        line_source.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line_source.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(width)
        return actor

# -------------- Optional main usage example --------------
if __name__ == "__main__":
    # Example workspace and DICOM folder
    slicer = AutoSlicer("TEST_WORKSPACE2")
    dicom_folder = r"D:\Curtin_Hive_Data\head-male female\1-1"
    #
    results = slicer.run_automation(dicom_folder)
    print("Final results:", results)

    # 2) Visualize with COM (if it exists in results)
    com = results["T4"]["value"]  # center of mass from pipeline
    slicer.visualize_with_coordinate_axes(original_com=com, decimate_ratio=0.3)