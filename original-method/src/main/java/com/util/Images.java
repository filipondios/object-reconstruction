package com.util;

import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.awt.image.ConvolveOp;
import java.awt.image.Kernel;
import java.util.ArrayList;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;

public class Images {

    private static int Black = 0x000000;
    private static int White = 0xffffff;
    private static int rgbMask = White;
   
    /**
     * Given a projection image of an object, process the image so that only the
     * contour of the figure is extracted. We assume the figure has black 
     * borders on a white background, and the surface of the object can be of 
     * any other color. The result should be an a black background where the 
     * pixels corresponding to the object's contour are represented in white.
     * @param img Projection image.
     * @return Image containing only the contour of the object.
     */
    public static BufferedImage getImageCountour(final BufferedImage img) {
        // STEP 1: Fill the projection interior gaps
        for (int i = 0; i < img.getHeight(); i++) {
            for (int j = 0; j < img.getWidth(); j++) {
                if ((img.getRGB(j, i) & rgbMask) != White)
                    img.setRGB(j, i, White);
                else img.setRGB(j, i, Black);
            }
        }

        // STEP 2: Get edges with the Laplacian kernel
        final float[] laplacian = { -1, -1, -1, -1,  8, -1, -1, -1, -1 };
        final Kernel kernel = new Kernel(3, 3, laplacian);
        return (new ConvolveOp(kernel, ConvolveOp.EDGE_NO_OP, null))
            .filter(img, null);
    }


    /**
     * Given an image of a projection of an object from which the contour line
     * has already been extracted—resulting in an image with a black background
     * and a closed white line—crop only that line and add a one-pixel 
     * border/margin to it. In this program, the input image is an output of the
     * {@link #getImageCountour(BufferedImage)} function.
     * @param img Image with a closed contour line.
     * @return Adjusted image.
     */
    public static BufferedImage preprocess(final BufferedImage img) {
        int min_row = Integer.MAX_VALUE, max_row = Integer.MIN_VALUE;
        int min_col = Integer.MAX_VALUE, max_col = Integer.MIN_VALUE;

        // Get object bounds within the image
        for (int i = 0; i < img.getHeight(); i++) {
            for (int j = 0; j < img.getWidth(); j++) {
                if((img.getRGB(j, i) & rgbMask) == Black) {
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
        final BufferedImage result = new BufferedImage(new_cols + 2, new_rows + 2, BufferedImage.TYPE_INT_RGB);
        
        final Graphics g = result.getGraphics();
        g.drawImage(crop, 1, 1, null);
        g.dispose();
        return result;
    }


    /**
     * Given an image with a black background and a closed black line that 
     * defines the contour of an object, obtain a polygonal line from the 
     * vertices of that contour. In this program, the input to this function is 
     * the result of the {@link #preprocess(BufferedImage)} function.
     * @param img An image with the object's contour line.
     * @return Polygonal line wich defines the object's contour.
     */
    public static Polygon getContourPolygon(final BufferedImage img) {
        final ArrayList<Coordinate> points = new ArrayList<>();
        int initial_x = -1, initial_z = 1;

        // Get the first vertex of the object contour.
        for (int i = 1; i < img.getWidth() - 1; i++) {
            if ((img.getRGB(i, initial_z) & rgbMask) == White) {
                initial_x = i;
                break;
            }
        }

        // Iterate over the pixels of the line that defines the contour of the 
        // projected object and obtain the coordinates of the vertices.

        final int[][] directions = new int[][] {{1,0}, {0,1}, {-1,0}, {0,-1}};
        int previous_x = initial_x, previous_z = initial_z;
        int current_x = initial_x, current_z = initial_z;

        final double z0 = img.getHeight()/2.0;
        final double x0 = img.getWidth()/2.0;
   
        do {
            // Verify if the current pixel is a vertex.
            final int horz = img.getRGB(current_x - 1, current_z) | img.getRGB(current_x + 1, current_z);
            final int vert = img.getRGB(current_x, current_z - 1) | img.getRGB(current_x, current_z + 1);

            if (((horz & rgbMask) == White) && ((vert & rgbMask) == White)) {
                // Translate (current_x, current_z) to 2D coordinates with 
                // the center of the image as origin (0, 0).
                points.add(new Coordinate(current_x - x0, z0 - current_z));
            }

            for (final int[] direction : directions) {
                final int next_x = current_x + direction[0];
                final int next_y = current_z + direction[1];

                if ((img.getRGB(next_x, next_y) & rgbMask) == White &&
                    !(next_x == previous_x && next_y == previous_z)) {
                    previous_x = current_x;
                    previous_z = current_z;
                    current_x = next_x;
                    current_z = next_y;
                    break;
                }
            }
        } while (!(current_x == initial_x && current_z == initial_z));
        
        final GeometryFactory factory = new GeometryFactory();
        points.add(points.get(0)); // close the polygon
        return factory.createPolygon(points.toArray(new Coordinate[0]));
    }
}