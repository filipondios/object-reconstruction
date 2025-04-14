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
import com.util.Segment;

public class View {

    public BufferedImage projection;
    public ViewCamera camera;
    public ArrayList<Segment<Vector2D>> edges;
    public ArrayList<Vector2D> vertices;

    public View(final String path) {
        try {
            this.projection = ImageIO.read(new File(path + "/plane.bmp"));
            this.projection = Images.preprocess(this.projection);
            this.camera = ViewCamera.deserializeFrom(path + "/camera.json");
            this.vertices = new ArrayList<>();
            this.vertices = new ArrayList<>();
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }

    public static ArrayList<Segment<Vector2D>> getRasterizationSegments(View view, Line common_line) {
        final ArrayList<Segment<Vector2D>> list = new ArrayList<>();

        // Calculate the direction of the rasterization segments. To do so, we
        // need to calculate the direction vector of a perpendicular line to the
        // common line that also passes through a point of the projection plane 
        // (in this case, the camera position of the view).

        final Vector3D q = common_line.getOrigin();
        final Vector3D v = common_line.getDirection();

        final Vector3D pq = view.camera.position.subtract(q);
        final double t = pq.dotProduct(v)/v.dotProduct(v);
        final Vector3D qPrime = q.add(v.scalarMultiply(t));
        final Vector3D direction = qPrime.subtract(view.camera.position);

        // Now that we have the direction of that perpendicular line, we need to
        // know wich of Vx or Vz has also the same direction, and then iterate 
        // horizontally or vertically over the projection image pixels.

        if (direction.crossProduct(view.camera.vx).equals(Vector3D.ZERO)) {
            // vx x direction = (0, 0, 0) means the rasterization lines follow 
            // vx (horizontal) lines.
            System.out.println("horizontal");
        }
        
        else if (direction.crossProduct(view.camera.vz).equals(Vector3D.ZERO)) {
            // vz x direction = (0, 0, 0) means the rasterization lines follow 
            // vx (vertical) lines.
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