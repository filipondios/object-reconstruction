package com.image;

import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import java.awt.image.BufferedImage;
import java.util.ArrayList;

public class ImageProcessing {

    public static final int PIXEL_BACKGROUND = 0x00;
    public static final int PIXEL_CONTOUR = 0xff;

    public static BufferedImage trimImage(BufferedImage img) {
        final int rows = img.getHeight();
        final int cols = img.getWidth();

        int min_row = Integer.MAX_VALUE, max_row = Integer.MIN_VALUE;
        int min_col = Integer.MAX_VALUE, max_col = Integer.MIN_VALUE;

        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                if((img.getRGB(i, j) & 0xff) == PIXEL_CONTOUR) {
                    // skip background (white) pixels
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
        return img.getSubimage(max_col, min_row, new_cols, new_rows);
    }

    public static ArrayList<Vector2D> extractVertices(final BufferedImage img) {
        ArrayList<Vector2D> vertices = new ArrayList<>();
        final int rows = img.getHeight();
        final int cols = img.getWidth();
        final int z0 = rows >> 1;
        final int x0 = cols >> 1;

        for (int zi = 1; zi < rows - 1; ++zi) {
            final int z_rel = z0 - zi;

            for (int xi = 1; xi < cols - 1; ++xi) {
                if((img.getRGB(xi, zi)& 0xff) == PIXEL_CONTOUR) {
                    // skip background (white) pixels
                    continue;
                }

                // Check if the current 3x3 pixel neighbourhood forms a contour
                // vertex at the current iteration pixel (xi, zi).
                final int hv = img.getRGB(xi, zi + 1) & img.getRGB(xi, zi - 1) & 0xff;
                final int vv = img.getRGB(xi - 1, zi) & img.getRGB(xi + 1, zi) & 0xff;

                if ((hv  == PIXEL_BACKGROUND) && (vv == PIXEL_BACKGROUND)) {
                    // Corner detected. The 3x3 pixel neighbourhood its not a
                    // horizontal or vertical line nor a isolated pixel).
                    vertices.add(new Vector2D(xi - x0, z_rel));
                }
            }
        }
        return vertices;
    }
}
