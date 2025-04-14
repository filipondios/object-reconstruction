package com.core;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Plane;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import com.util.Images;
import com.util.Polygon;
import com.util.Segment;
import de.vandermeer.asciitable.AsciiTable;
import de.vandermeer.skb.interfaces.transformers.textformat.TextAlignment;

public class Model {

    public ArrayList<View> views;
    public HashMap<Plane, ArrayList<Polygon<Vector3D>>> planes;
    public String path;

    public Model(final String path) {
        this.views = new ArrayList<>();
        this.planes = new HashMap<>();
        this.path = path;
        
        Arrays.stream(new File(path).listFiles())
            .filter(File::isDirectory)
            .map(File::getAbsolutePath)
            .filter(View::isViewDir)
            .map(View::new)
            .forEach(this.views::add);
    }

    public void initialReconstruction() {
        if (this.views.size() < 2) {
            // nothing to do
            return;
        }

        View view1 = this.views.get(0);
        View view2 = null;

        for (int i = 1; i < this.views.size(); i++) {
            final View view = this.views.get(i);
            
            if (!view1.camera.vy.crossProduct(view.camera.vy)
                .equals(Vector3D.ZERO)) {
                view2 = view;
                break;
            }
        }

        if (view2 == null) {
            // nothing to do
            return;
        }

        // Once we have two views with no parallell view planes, we can proceed. First,
        // we must get the common line between both view planes by intersecting them.

        final Line commonLine = (new Plane(view1.camera.position, view1.camera.vy, 1e-10))
            .intersection(new Plane(view2.camera.position, view2.camera.vy, 1e-10));
        
        // Now we have to calculate the set of rasterization segments in each view image
        // plane. Those segments will be used to make contour generation lines.

        final ArrayList<Segment<Vector2D>> rasterizationSegments1 
        = null;
        //= Images.getRasterizationSegments(view1, commonLine);
        final ArrayList<Segment<Vector2D>> rasterizationSegments2 
        //    = Images.getRasterizationSegments(view2, commonLine);
        = null;
        
        // The last step is to intersect all the possible pairs of contour generation 
        // lines produced by each rasterizatrion segment in both views.

        for (final Segment<Vector2D> segment1 : rasterizationSegments1) {

            // Obtener las lineas generadoras de contorno a partir de los extremos
	        // del segmento de rasterizacion perteneciente a la vista1.

            final Vector3D src1 = view1.planeToRealPoint(segment1.src);
            final Vector3D dst1 = view1.planeToRealPoint(segment1.dst);
            final Line contourGenV1_1 = new Line(src1, src1.add(view1.camera.vy), 1e-10);
            final Line contourGenV1_2 = new Line(dst1, dst1.add(view1.camera.vy), 1e-10);

            // Obtener la lista de poligonos del plano en el que esta contenido el
	        // segmento de rasterizacion actual.            
            
            final Plane plane = new Plane(src1, commonLine.getDirection(), 1e-10);
            ArrayList<Polygon<Vector3D>> polygons = this.planes.get(plane);

            for (final Segment<Vector2D> segment2 : rasterizationSegments2) {

                // Obtener las lineas generadoras de contorno a partir de los extremos
	            // del segmento de rasterizacion perteneciente a la vista2.
 
                final Vector3D src2 = view1.planeToRealPoint(segment2.src);
                final Vector3D dst2 = view1.planeToRealPoint(segment2.dst);
            
                if (!(plane.contains(src2) && plane.contains(dst2))) {
                    // Omitir el segmento si no es coplanar
                    continue;
                }

                final Line contourGenV2_1 = new Line(src2, src2.add(view2.camera.vy), 1e-10);
                final Line contourGenV2_2 = new Line(dst2, dst2.add(view2.camera.vy), 1e-10);

                // Calcular la interseccion de las lineas generadoras de contorno de las 
                // vistas 1 y 2, que resultan en cuatro intersecciones en total. Los 
                // puntos de interseccion definen un nuevo poligono, concretamente un
                // paralelogramo.
                
                final ArrayList<Vector3D> points = new ArrayList<>(4);
                points.add(contourGenV1_1.intersection(contourGenV2_1));
                points.add(contourGenV1_1.intersection(contourGenV2_2));
                points.add(contourGenV1_2.intersection(contourGenV2_1));
                points.add(contourGenV1_2.intersection(contourGenV2_2));
                final Polygon<Vector3D> polygon = new Polygon<>(points);

                if (polygons == null) {
                    polygons = new ArrayList<>();
                    polygons.add(polygon);
                    this.planes.put(plane, polygons);
                } else {
                    polygons.add(polygon);
                }
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