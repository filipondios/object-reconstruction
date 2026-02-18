# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-02-18

### Added

- New `utils/geo3d.py` module with pure NumPy geometry functions:
    - `intersect_lines()` - Fast 3D line intersection using least squares.
    - `point_on_plane()` - Coplanarity check with configurable tolerance.
    - `project_point_to_plane()` - Orthogonal point projection.
    - `planes_intersection()` - Intersection line between two planes.
    - `intersect_3dpolygons()` - Coplanar 3D polygon intersection.
    - `Axis` enum for axis-aligned operations.
    - `Plane` enum for plane-aligned operations.

- Vectorized operations in simple algorithm:
    - `View.real_to_plane_batch()` - Batch coordinate transformation
    - `View.points_inside_polygon_batch()` - Vectorized polygon containment checks
    - `View.polygon_view_to_plane()` - Efficient 2D view-to-plane coordinate conversion

### Optimized

- Complex Algorithm
    - **99.3% performance improvement** for complex models.
    - Replaced symbolic SymPy operations with numerical NumPy operations.
    - Pre-grouped segments by axis-aligned keys to avoid O(n²) comparisons in `initial_reconstruction()`.
    - Cached `dst2` coordinates in segment dictionary to eliminate redundant `plane_to_real()` calls.
    - Eliminated redundant 3D-to-2D projections in `refine_model()`:
        - View polygon now converted directly to plane 2D coordinates.
        - Removed intermediate 3D conversion that was immediately discarded.
        - Only calculates required 2D components based on projection axis.
        - Cached Shapely `Polygon` objects for view polygons to avoid recreation per plane.

- Simple Algorithm
    - **74.3% performance improvement** for complex models.
    - Fully vectorized `project_view_to_voxels()`:
        - Replaced nested loops with `np.meshgrid()` operations.
        - Batch coordinate transformations using matrix multiplication.
        - Vectorized polygon containment checks using Shapely's accelerated functions.
    - Fully vectorized `generate_surface()`:
        - Replaced triple nested loop with `np.argwhere()` and vectorized coordinate calculation.

### Removed

- Removed dependency on SymPy for geometric operations.
- Removed `complex/model.py` dependency on `sympy.Plane`, `sympy.Matrix`, `sympy.Line3D`, `sympy.Point3D`.
- Removed `simple/view.py` dependency on `sympy.Matrix`.


## [1.0.0] - 2025-07-17

### Added

- Initial release with complex and simple reconstruction algorithms
- Support for multi-view 3D reconstruction from 2D orthographic projections
- Interactive 3D visualization with camera controls
- Command-line interface for model reconstruction

[1.1.0]: https://github.com/filipondios/object-reconstruction/tree/refs/tags/v1.1.0
[1.0.0]: https://github.com/filipondios/object-reconstruction/tree/refs/tags/v1.0.0