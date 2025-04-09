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
    public HashMap<Plane, ArrayList<Polygon>> planes;
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

        for (final View view : this.views) {
            // todo iterate with i>0
            Vector3D vec = view1.camera.vy
                .crossProduct(view.camera.vy);

            if (!vec.equals(Vector3D.ZERO)) {
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
            = Images.getRasterizationSegments(view1, commonLine);
        final ArrayList<Segment<Vector2D>> rasterizationSegments2 
            = Images.getRasterizationSegments(view2, commonLine);

        
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