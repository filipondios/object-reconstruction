package com.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;

import javax.imageio.ImageIO;

import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
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

    @Test
    public void testGetContourPolygon() throws IOException {
        final String[] names = { "polygon1", "polygon2" };
        BufferedImage img;
        ArrayList<Vector2D> polyLine;
        Polygon<Vector2D> polygon;
        
        // Process the first image (a simple square).
        polyLine = new ArrayList<>(Arrays.asList(
            new Vector2D(-4,4),
            new Vector2D(4,4),
            new Vector2D(4,-4),
            new Vector2D(-4,-4)
        ));

        img = ImageIO.read(new File("tests-dir/" + names[0] + ".png"));
        polygon = Images.getContourPolygon(img);
        assertEquals(polyLine, polygon.points);

        // Process the second image (a more complex line).
        polyLine = new ArrayList<>(Arrays.asList(
            new Vector2D(-9,9),
            new Vector2D(9,9),
            new Vector2D(9,-9),
            new Vector2D(-4,-9),
            new Vector2D(-4,-5),
            new Vector2D(-1,-5),
            new Vector2D(-1,-1),
            new Vector2D(-4,-1),
            new Vector2D(-4,4),
            new Vector2D(-9,4)
        ));

        img = ImageIO.read(new File("tests-dir/" + names[1] + ".png"));
        polygon = Images.getContourPolygon(img);
        assertEquals(polyLine, polygon.points);
    }
}