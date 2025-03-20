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
    public transient BufferedImage plane;
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

    public Vector3D planeToRealPoint(Vector2D point) {
        final double x = point.getX();
        final double z = point.getY();
        // (x,z) -> (xi, yi, zi) = position + x * vx + z * vz
        return this.position.add(vx.scalarMultiply(x)).add(vz.scalarMultiply(z));
    }

    public Vector2D realToPlanePoint(final Vector3D point) {
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
            point.getY() - this.position.getY(),
            point.getZ() - this.position.getZ(),
        });

        final RealVector solution = new QRDecomposition(coefficients)
            .getSolver().solve(constansts);
        return new Vector2D(solution.getEntry(0), solution.getEntry(1));
    }

    public Vector2D planeToImageCoord(Vector2D point) {
        final int x = (int) point.getX() + (this.plane.getWidth()  >> 1);
        final int z = -((int) point.getY() - (this.plane.getHeight() >> 1)); 
        return new Vector2D(x, z);
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