package com.util;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;
import org.junit.jupiter.api.Test;

public class TestImages {

    @Test
    void testGetImageContour() throws IOException {
        final String[] names = { "contour1", "contour2", "contour3" };
        BufferedImage img;
        File file;

        for (final String name : names) {
            // Read -> Preprocess -> Write (No assert)
            file = new File("tests-dir/" + name + ".png");
            img = ImageIO.read(file);
            img = Images.getImageCountour(img);
            file = new File("tests-dir/" + name + "-result.png");
            ImageIO.write(img, "png", file);
        }
    }

    @Test
    public void testPreprocessImage() throws IOException {
        final String[] names = { "preprocess1", "preprocess2", "preprocess3" };
        BufferedImage img;
        File file;

        for (final String name : names) {
            // Read -> Preprocess -> Write (No assert)
            file = new File("tests-dir/" + name + ".png");
            img = ImageIO.read(file);
            img = Images.preprocess(img);
            file = new File("tests-dir/" + name + "-result.png");
            ImageIO.write(img, "png", file);
        }
    }
}