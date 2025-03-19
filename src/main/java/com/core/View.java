package com.core;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import org.apache.commons.math3.linear.*;
import com.image.ImageProcessing;
import java.util.ArrayList;
import java.awt.image.BufferedImage;

public class View {

    public Vector3D position;
    public Vector3D vx;
    public Vector3D vy;
    public Vector3D vz;
    private transient BufferedImage plane;
    public transient ArrayList<Vector3D> vertices;
    public String name;

    public void setViewPlane(BufferedImage image) {
        //image = ImageProcessing.trimImage(image);
        this.vertices = new ArrayList<>();
        this.plane = image;

        ImageProcessing.extractVertices(image).forEach(point -> {
            this.vertices.add(this.planeToRealPoint(point));
        });
    }

    private Vector3D planeToRealPoint(Vector2D point) {
        final double x = point.getX();
        final double z = point.getY();
        // (x,z) -> (xi, yi, zi) = position + x * vx + z * vz
        return this.position.add(vx.scalarMultiply(x)).add(vz.scalarMultiply(z));
    }

    public int realToPlanePoint(final Vector3D point) {
        // Calculate the translation of the point (x, y, z) inside the image 
        // plane as a (x, z) point inside the image. This leads to solving the
        // following ecuation system (used in point3DFromImage):
        //
        // xi = x * vx.x + z * vz.x + position.x
        // yi = x * vx.y + z * vz.y + position.y
        // zi = x * vx.z + z * vz.z + position.z
        //
        // Which is the same as:
        //
        // x * vx.x + z * vz.x = xi - position.x 
        // x * vx.y + z * vz.y = yi - position.y
        // x * vx.z + z * vz.z = zi - position.z

        final RealMatrix coefficients = 
            new Array2DRowRealMatrix(new double[][] {
            { this.vx.getX(), this.vz.getX() },
            { this.vx.getY(), this.vz.getY() },
            { this.vx.getZ(), this.vz.getZ() },
        });

        final RealVector constansts = 
            new ArrayRealVector(new double[] {
            point.getX() - this.position.getX(),
            point.getY() - this.position.getX(),
            point.getZ() - this.position.getX(),
        });

        final RealVector solution = new QRDecomposition(coefficients)
            .getSolver().solve(constansts);
        final int x = (int) solution.getEntry(0);
        final int z = (int) solution.getEntry(1);
        return this.plane.getRGB(x, z) & 0xff;
    }

    @Override
    public String toString() {
        return "[View: " + this.name + "]\n" + 
            "Position: " + this.position + "\n" + 
            "Vx: " + this.vx + "\n" +
            "Vy: " + this.vy + "\n" +
            "Vz: " + this.vz + "\n" + 
            "Vertices: " + this.vertices.size() + "\n";
    }
}