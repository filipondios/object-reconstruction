package com.core;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.QRDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;
import org.locationtech.jts.geom.Polygon;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.LineString;
import org.locationtech.jts.geom.MultiLineString;
import com.util.Images;

public class View {

    public final ViewCamera camera;
    public final Polygon polygon;
    public final BufferedImage projection;

    public View(final String path) throws IOException {
        // Read the projection plane image and the camera data.
        this.camera = ViewCamera.deserializeFrom(path + "/camera.json");
        BufferedImage img = ImageIO.read(new File(path + "/plane.bmp"));
        img = Images.getImageCountour(img);
        img = Images.preprocess(img);
        this.polygon = Images.getContourPolygon(img); 
        this.projection = img;
    }

    public ArrayList<LineString> rasterizationSegments(final Line common_line, final double step) {
        // Calculate the direction of the segments
        final Vector3D q = common_line.getOrigin();
        final Vector3D v = common_line.getDirection();
        final Vector3D pq = this.camera.position.subtract(q);

        final double t = pq.dotProduct(v)/v.dotProduct(v);
        final Vector3D qPrime = q.add(v.scalarMultiply(t));
        final Vector3D direction = qPrime.subtract(this.camera.position);

        final int width  = this.projection.getWidth();
        final int height = this.projection.getHeight(); 

        // Calculate the view polygon bounds
        final ArrayList<LineString> segments = new ArrayList<>();
        final GeometryFactory factory = new GeometryFactory();

        final double minX = 1 - (width/2.0f);
        final double maxX = (width - 2) - (width/2.0f);
        final double minZ = (height/2.0f) - (height - 2);
        final double maxZ = (height/2.0f) - 1;

        if (direction.crossProduct(this.camera.vx).getNorm() <= 1e-6) {
            // This means the rasterization lines are horizontal
            for (double z = minZ; z <= maxZ; z += step) { 
                final Geometry intersection = this.polygon.intersection(
                    factory.createLineString(
                        new Coordinate[] {
                            new Coordinate(minX - 1e4, z),
                            new Coordinate(maxX + 1e4, z)
                        }
                    )
                );

                if (intersection.isEmpty())
                    continue;

                if (intersection instanceof LineString)
                    segments.add((LineString) intersection);
                
                else if (intersection instanceof MultiLineString) {
                    for (int i = 0; i < intersection.getNumGeometries(); i++) {
                        segments.add((LineString) intersection.getGeometryN(i));
                    }
                }
            }
        }      
        else if (direction.crossProduct(this.camera.vz).getNorm() <= 1e-6) {
            // This means the rasterization lines are horizontal
            for (double x = minX; x <= maxX; x += step) { 
                final Geometry intersection = this.polygon.intersection(
                    factory.createLineString(
                        new Coordinate[] {
                            new Coordinate(x, minZ - 1e4),
                            new Coordinate(x, maxZ + 1e4)
                        }
                    )
                );

                if (intersection.isEmpty())
                    continue;

                if (intersection instanceof LineString)
                    segments.add((LineString) intersection);
                
                else if (intersection instanceof MultiLineString) {
                    for (int i = 0; i < intersection.getNumGeometries(); i++) {
                        segments.add((LineString) intersection.getGeometryN(i));
                    }
                }
            }
        } else { /*To-do this must be unrecheable*/ }
        return segments;
    }

    public Vector3D planeToRealPoint(final Coordinate point) {
        // (x,z) -> (xi,yi,zi) = origin + x*vx + z*vz
        return this.camera.position
            .add(this.camera.vx.scalarMultiply(point.x))
            .add(this.camera.vz.scalarMultiply(point.y));
    }

    public Coordinate realToPlanePoint(final Vector3D point) {
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
            { this.camera.vx.getX(), this.camera.vz.getX() },
            { this.camera.vx.getY(), this.camera.vz.getY() },
            { this.camera.vx.getZ(), this.camera.vz.getZ() },
        });

        final RealVector constansts = 
            new ArrayRealVector(new double[] {
            point.getX() - this.camera.position.getX(),
            point.getY() - this.camera.position.getY(),
            point.getZ() - this.camera.position.getZ(),
        });

        final RealVector solution = new QRDecomposition(coefficients)
            .getSolver().solve(constansts);
        return new Coordinate(solution.getEntry(0), solution.getEntry(1));
    }

    @Override
    public String toString() {
        return this.camera.name;
    }
}