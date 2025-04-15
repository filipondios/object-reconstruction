package com.core;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import com.util.Images;
import com.util.Polygon;
import com.util.Segment;

public class View {

    public final Polygon<Vector2D> polygon;
    public final ViewCamera camera;

    public View(final String path) throws IOException {
        // Read the projection plane image and the camera data.
        this.camera = ViewCamera.deserializeFrom(path + "/camera.json");
        BufferedImage img = ImageIO.read(new File(path + "/plane.bmp"));
        img = Images.getImageCountour(img);
        img = Images.preprocess(img);
        this.polygon = Images.getContourPolygon(img);    
    }

    public ArrayList<Segment<Vector2D>> getRasterizationSegments(Line common_line) {
        final ArrayList<Segment<Vector2D>> list = new ArrayList<>();

        // Calculate the direction of the rasterization segments. To do so, we
        // need to calculate the direction vector of a perpendicular line to the
        // common line that also passes through a point of the projection plane 
        // (in this case, the camera position of the view).

        final Vector3D q = common_line.getOrigin();
        final Vector3D v = common_line.getDirection();

        final Vector3D pq = this.camera.position.subtract(q);
        final double t = pq.dotProduct(v)/v.dotProduct(v);
        final Vector3D qPrime = q.add(v.scalarMultiply(t));
        final Vector3D direction = qPrime.subtract(this.camera.position);

        // Now that we have the direction of that perpendicular line, we need to
        // know wich of Vx or Vz has also the same direction, and then iterate 
        // horizontally or vertically over the projection image pixels.

        if (direction.crossProduct(this.camera.vx).equals(Vector3D.ZERO)) {
            // This means the rasterization lines follow (horizontal) lines.
            System.out.println("horizontal");
        }
        
        else if (direction.crossProduct(this.camera.vz).equals(Vector3D.ZERO)) {
            // This means the rasterization lines follow (horizontal) lines.
            System.out.println("vertical");
        }

        else { /* This must be unreachable */ }       
        return list;
    }

    public static boolean isViewDir(final String path) {
        return (new File(path + "/camera.json").isFile())
            && (new File(path + "/plane.bmp").isFile());
    }

    public Vector3D planeToRealPoint(final Vector2D point) {
        // (x,z) -> (xi,yi,zi) = origin + x*vx + z*vz
        final double x = point.getX();
        final double z = point.getY();
        
        return this.camera.position
            .add(this.camera.vx.scalarMultiply(x))
            .add(this.camera.vz.scalarMultiply(z));
    }

    public Vector2D realToPlanePoint(final Vector3D point) {
        return null;
    }

    @Override
    public String toString() {
        return this.camera.name;
    }
}