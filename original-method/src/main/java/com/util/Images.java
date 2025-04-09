package com.util;

import java.awt.image.BufferedImage;
import java.awt.image.ConvolveOp;
import java.awt.image.Kernel;
import java.util.ArrayList;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import com.core.View;

public class Images {

    /// Given a projection image of an object, process this image so that
    /// only the contour of the figure is subtracted.
    ///
    /// We assume that the figure has black borders, on a white background,
    /// and the surface of the object has any other colour (look at the 
    /// views (plane.bmp) of the different models in the directory "models").
    /// 
    /// The result will be a image with a black background and the pixels 
    /// from the object contour represented as white.
    
    public static BufferedImage getImageCountour(final BufferedImage img) {
        final int white = 0xffffff;
        final int black = 0x000000;
        final int rgbMask = white;

        // STEP 1: Fill the projection interior gaps
        for (int i = 0; i < img.getHeight(); i++) {
            for (int j = 0; j < img.getWidth(); j++) {
                if ((img.getRGB(j, i) & rgbMask) == white)
                    img.setRGB(j, i, black);
                else img.setRGB(j, i, white);
            }
        }

        // STEP 2: Get edges with the Laplacian kernel
        final float[] laplacian = { -1, -1, -1, -1,  8, -1, -1, -1, -1 };
        final Kernel kernel = new Kernel(3, 3, laplacian);
        return (new ConvolveOp(kernel, ConvolveOp.EDGE_NO_OP, null))
            .filter(img, null);
    }

    public static ArrayList<Segment<Vector2D>> getRasterizationSegments(View view, Line common_line) {
        ArrayList<Segment<Vector2D>> list = new ArrayList<>();

        // Calculate the direction of the rasterization segments. To do so, we need to
        // calculate the direction vector of a perpendicular line to the common line
        // that also passes through a point of the projection plane (in this case, the
        // camera position of the view).

        final Vector3D q = common_line.getOrigin();
        final Vector3D v = common_line.getDirection();

        final Vector3D pq = view.camera.position.subtract(q);
        final double t = pq.dotProduct(v)/v.dotProduct(v);
        final Vector3D qPrime = q.add(v.scalarMultiply(t));
        final Vector3D direction = qPrime.subtract(view.camera.position);

        // Now that we have the direction of that perpendicular line, we need to know
        // wich of Vx or Vz has also the same direction, and then iterate horizontally
        // or vertically over the projection image pixels.

        if (direction.crossProduct(view.camera.vx).equals(Vector3D.ZERO)) {
            // vx x direction = (0, 0, 0) means the rasterization lines follow vx
            // (horizontal) lines.
            System.err.println("horizontal");
        }
        
        else if (direction.crossProduct(view.camera.vz).equals(Vector3D.ZERO)) {
            // vz x direction = (0, 0, 0) means the rasterization lines follow vx
            // (vertical) lines.
            System.err.println("vertical");
        }

        else { /* This must be unreachable */ }       
        return list;
    }
}