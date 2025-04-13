package com.core;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import javax.imageio.ImageIO;
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