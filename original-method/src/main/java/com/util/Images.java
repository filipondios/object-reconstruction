package com.util;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.awt.image.ConvolveOp;
import java.awt.image.Kernel;
import java.util.ArrayList;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import com.core.View;

public class Images {

    private static int Black = 0x000000;
    private static int White = 0xffffff;
    private static int rgbMask = White;


    /// Dada una imagen de una vista, recortar solo la figura del objeto
    /// y anadirle un borde de un pixel. Despues, solo preservar los bordes.
    
    public static BufferedImage preprocess(final BufferedImage img) {
        int min_row = Integer.MAX_VALUE, max_row = Integer.MIN_VALUE;
        int min_col = Integer.MAX_VALUE, max_col = Integer.MIN_VALUE;

        // Get object bounds
        for (int i = 0; i < img.getHeight(); i++) {
            for (int j = 0; j < img.getWidth(); j++) {
                if((img.getRGB(j, i) & 0xffffff) != 0xffffff) {
                    // skip non-border pixels
                    continue;
                }

                if (i < min_row) min_row = i;
                if (i > max_row) max_row = i;
                if (j < min_col) min_col = j;
                if (j > max_col) max_col = j;
            }
        }

        final int new_cols = max_col - min_col + 1;
        final int new_rows = max_row - min_row + 1;
        final BufferedImage crop = img.getSubimage(min_col, min_row, new_cols, new_rows);
        final BufferedImage result = new BufferedImage(new_cols + 2, new_rows + 2, crop.getType());
        
        final Graphics g = result.getGraphics();
        g.drawImage(crop, 1, 1, null);
        g.dispose();
        return getImageCountour(result);
    }

    /// Given a projection image of an object, process this image so that
    /// only the contour of the figure is subtracted.
    ///
    /// We assume that the figure has black borders, on a white background,
    /// and the surface of the object has any other colour (look at the 
    /// views (plane.bmp) of the different models in the directory "models").
    /// 
    /// The result will be a image with a black background and the pixels 
    /// from the object contour represented as white.
    
    private static BufferedImage getImageCountour(final BufferedImage img) {
        // STEP 1: Fill the projection interior gaps
        for (int i = 0; i < img.getHeight(); i++) {
            for (int j = 0; j < img.getWidth(); j++) {
                if ((img.getRGB(j, i) & rgbMask) == White)
                    img.setRGB(j, i, Black);
                else img.setRGB(j, i, White);
            }
        }

        // STEP 2: Get edges with the Laplacian kernel
        final float[] laplacian = { -1, -1, -1, -1,  8, -1, -1, -1, -1 };
        final Kernel kernel = new Kernel(3, 3, laplacian);
        return (new ConvolveOp(kernel, ConvolveOp.EDGE_NO_OP, null))
            .filter(img, null);
    }


    public static Polygon<Vector2D> getContourPolygon(final BufferedImage img) {
        final ArrayList<Vector2D> points = new ArrayList<>();
        int initial_x = -1, initial_y = 1;

        // Get the first vertex of the object contour
        for (int i = 1; i < img.getWidth() - 1; i++) {
            if ((img.getRGB(i, initial_y) & rgbMask) == White) {
                initial_x = i;
                break;
            }
        }

        // Iterar por los pixeles de la linea que define el contorno del objeto
        // proyectado y obtener las coordenadas de los vertices de dicha linea.

        final int[][] directions = new int[][] {{1,0}, {0,1}, {-1,0}, {0,-1}};
        int previous_x = initial_x, previous_y = initial_y;
        int current_x = initial_x, current_y = initial_y;
   
        do {
            // Verify if the current pixel is a vertex. If it is, add it to the polygon.
            final int horz = img.getRGB(current_x - 1, current_y) | img.getRGB(current_x + 1, current_y);
            final int vert = img.getRGB(current_x, current_y - 1) | img.getRGB(current_x, current_y + 1);

            if (((horz & rgbMask) == White) && ((vert & rgbMask) == White)) {
                points.add(new Vector2D(current_x, current_y));
            }

            for (final int[] direction : directions) {
                final int next_x = current_x + direction[0];
                final int next_y = current_y + direction[1];

                if ((img.getRGB(next_x, next_y) & rgbMask) == White &&
                    !(next_x == previous_x && next_y == previous_y)) {
                    previous_x = current_x;
                    previous_y = current_y;
                    current_x = next_x;
                    current_y = next_y;
                    break;
                }
            }
        } while (!(current_x == initial_x && current_y == initial_y));
        return new Polygon<Vector2D>(points);
    }


    public static ArrayList<Segment<Vector2D>> getRasterizationSegments(View view, Line common_line) {
        final ArrayList<Segment<Vector2D>> list = new ArrayList<>();

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