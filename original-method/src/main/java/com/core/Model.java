package com.core;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map.Entry;

import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Plane;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.LineString;
import org.locationtech.jts.geom.Polygon;

import de.vandermeer.asciitable.AsciiTable;
import de.vandermeer.skb.interfaces.transformers.textformat.TextAlignment;

public class Model {

    public ArrayList<View> views;
    public HashMap<Plane, ArrayList<ArrayList<Vector3D>>> planes;
    public String path;

    public Model(final String path) throws IOException {
        this.views = new ArrayList<>();
        this.planes = new HashMap<>();
        this.path = path;
        
        Arrays.stream(new File(path).listFiles())
            .filter(File::isDirectory)
            .map(File::getAbsolutePath)
            .map(t -> {
                try {
                    return new View(t);
                } catch (IOException e) {
                    e.printStackTrace();
                    System.exit(-1);
                } return null; 
            }) .forEach(this.views::add);
    }

    public void initialReconstruction(final double step) {
        if (this.views.size() < 2)
            return;

        final View view1 = this.views.get(0);
        final View view2 = this.views.stream()
            .skip(1).filter(view -> {
                final Vector3D cross = view1.camera.vy.crossProduct(view.camera.vy); 
                return cross.getNorm() > 1e-6;
            }).findFirst().orElse(null);

        if (view2 == null)
            return;
        
        // Find the common line between views
        final Plane plane1 = new Plane(view1.camera.position, view1.camera.vy, 1e-6);
        final Plane plane2 = new Plane(view2.camera.position, view2.camera.vy, 1e-6);
        final Line commonLine = plane1.intersection(plane2);

        // Calculate both views rasterization lines
        final ArrayList<LineString> segments1 = view1.rasterizationSegments(commonLine, step);
        final ArrayList<LineString> segments2 = view2.rasterizationSegments(commonLine, step);

        for (final LineString segment1 : segments1) {
            // Contour generation lines for view1 segment
            final Vector3D src1 = view1.planeToRealPoint(segment1.getCoordinateN(0));
            final Vector3D dst1 = view1.planeToRealPoint(segment1.getCoordinateN(1));
            final Line contourGenV1_1 = new Line(src1, src1.add(view1.camera.vy), 1e-6);
            final Line contourGenV1_2 = new Line(dst1, dst1.add(view1.camera.vy), 1e-6);

            // Create plane containing the segment and parallel to common line
            final Plane plane = new Plane(src1, commonLine.getDirection(), 1e-6);
            ArrayList<ArrayList<Vector3D>> polygons = this.planes.get(plane);

            for (final LineString segment2 : segments2) {
                // Convert segment2 points using view2 (not view1!)
                final Vector3D src2 = view2.planeToRealPoint(segment2.getCoordinateN(0));
                final Vector3D dst2 = view2.planeToRealPoint(segment2.getCoordinateN(1));

                // Skip if segment is not in the plane (coplanar check)
                if (Math.abs(plane.getOffset(src2)) > 1e-6) {
                    continue;
                }

                // Contour generation lines for view2 segment
                final Line contourGenV2_1 = new Line(src2, src2.add(view2.camera.vy), 1e-6);
                final Line contourGenV2_2 = new Line(dst2, dst2.add(view2.camera.vy), 1e-6);

                // Calculate all 4 intersection points and create a polygon.
                final ArrayList<Vector3D> polygon = new ArrayList<>(Arrays.asList(
                    contourGenV1_1.intersection(contourGenV2_1),
                    contourGenV1_1.intersection(contourGenV2_2),
                    contourGenV1_2.intersection(contourGenV2_2),
                    contourGenV1_2.intersection(contourGenV2_1)
                ));

                if (polygons == null) {
                    polygons = new ArrayList<>();
                    this.planes.put(plane, polygons);
                }

                polygon.add(polygon.get(0));
                polygons.add(polygon);
            }
        }
    }

    public void refineModel() {
        if (this.views.size() < 3)
            return;

        final GeometryFactory factory = new GeometryFactory();

        for (int i = 2; i < this.views.size(); i++) {
            final View view = this.views.get(i);

            for (final Entry<Plane, ArrayList<ArrayList<Vector3D>>> entry : this.planes.entrySet()) {
                final ArrayList<ArrayList<Vector3D>> refinedPolygons = new ArrayList<>();
                final Plane plane = entry.getKey();
                
                for (ArrayList<Vector3D> polygon3d : entry.getValue()) {
                    // Project and refine the current polygon via intersection
                    final Coordinate[] coordinates = new Coordinate[polygon3d.size()];

                    for (int j = 0; j < coordinates.length; j++)
                        coordinates[j] =  view.realToPlanePoint(polygon3d.get(j));
                        
                    final Polygon polygon =  factory.createPolygon(coordinates);
                    final Geometry intersection = view.polygon.intersection(polygon);

                    if (intersection.isEmpty() || !(intersection instanceof Polygon))
                        continue; // Discard the polygon from the list.

                    // Traduce 2D intersection coordinates to 3D coordinates
                    final ArrayList<Vector3D> refined = new ArrayList<>();

                    for (final Coordinate point : ((Polygon) intersection).getCoordinates()) {
                        final Vector3D real = view.planeToRealPoint(point);
                        refined.add((Vector3D) plane.project(real));
                    }
                    refinedPolygons.add(refined);
                }
                this.planes.put(plane, refinedPolygons);
            }
        }
    }

    @Override
    public String toString() {
        String result;
        
        AsciiTable table = new AsciiTable();
        table.addRule();
        table.addRow(this.path);
        table.setTextAlignment(TextAlignment.CENTER);
        result = table.render();

        table = new AsciiTable();
        table.addRule();
        table.addRow("View", "Origin", "Vx", "Vy", "Vz");
        table.addRule();

        for (View camera : this.views) {
            table.addRow(
                camera.camera.name,
                camera.camera.position,
                camera.camera.vx,
                camera.camera.vy,
                camera.camera.vz
            );
        }

        table.addRule();
        return "\n" + result + "\n" + table.render();
    }
}