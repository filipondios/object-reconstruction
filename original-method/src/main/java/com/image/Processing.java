package com.image;

import java.awt.image.BufferedImage;
import java.awt.image.ConvolveOp;
import java.awt.image.Kernel;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

public class Processing {

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

    
}