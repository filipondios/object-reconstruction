package com.util;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.ArrayList;
import java.util.Arrays;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;

public class TestsVatti {
    
    @Test
    public void testClipRectangles() {
        ArrayList<Vector2D> subjectPoints;
        Polygon<Vector2D> subject;
        ArrayList<Vector2D> clipPoints;
        Polygon<Vector2D> clip;
        Polygon<Vector2D> result;
        ArrayList<Vector2D> resultPoints;
        
        // Test the clip between two squares.
        subjectPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(2, 1),
            new Vector2D(2, 3),
            new Vector2D(4, 3),
            new Vector2D(4, 1)
        ));

        clipPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(3, 2),
            new Vector2D(3, 5),
            new Vector2D(6, 5),
            new Vector2D(6, 2)
        ));

        resultPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(3, 3),
            new Vector2D(4, 3),
            new Vector2D(4, 2),
            new Vector2D(3, 2)
        ));

        subject = new Polygon<>(subjectPoints);
        clip = new Polygon<>(clipPoints);
        result = VattiClipper.clip(subject, clip);
        assertEquals(resultPoints, result.points);
        
        // Test if clipping a polygon with itself must
        // returns the same polygon (Order changes).

        resultPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(2, 3),
            new Vector2D(4, 3),
            new Vector2D(4, 1),
            new Vector2D(2, 1)
        ));

        result = VattiClipper.clip(subject, subject);
        assertEquals(resultPoints, result.points);
    }

    @Test
    public void testClipComplexPolygon() {
        ArrayList<Vector2D> subjectPoints;
        Polygon<Vector2D> subject;
        ArrayList<Vector2D> clipPoints;
        Polygon<Vector2D> clip;
        Polygon<Vector2D> result;
        ArrayList<Vector2D> resultPoints;
        
        // A cross-shaped polygon and a rectangle as clip
        subjectPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(0, 1),
            new Vector2D(0, 2),
            new Vector2D(1, 2),
            new Vector2D(1, 3),
            new Vector2D(2, 3),
            new Vector2D(2, 2),
            new Vector2D(3, 2),
            new Vector2D(3, 1),
            new Vector2D(2, 1),
            new Vector2D(2, 0),
            new Vector2D(1, 0),
            new Vector2D(1, 1)
        ));

        clipPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(0, 1),
            new Vector2D(0, 2),
            new Vector2D(3, 2),
            new Vector2D(3, 1)
        ));

        resultPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(0, 2),
            new Vector2D(1, 2),
            new Vector2D(2, 2),
            new Vector2D(3, 2),
            new Vector2D(3, 1),
            new Vector2D(2, 1),
            new Vector2D(1, 1),
            new Vector2D(0, 1)
        ));

        subject = new Polygon<>(subjectPoints);
        clip = new Polygon<>(clipPoints);
        result = VattiClipper.clip(subject, clip);
        assertEquals(resultPoints, result.points);

        // Test if clipping the complex polygon with 
        // itself returns the same polygon.

        resultPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(0, 2),
            new Vector2D(1, 2),
            new Vector2D(1, 3),
            new Vector2D(2, 3),
            new Vector2D(2, 2),
            new Vector2D(3, 2),
            new Vector2D(3, 1),
            new Vector2D(2, 1),
            new Vector2D(2, 0),
            new Vector2D(1, 0),
            new Vector2D(1, 1),
            new Vector2D(0, 1)
        ));

        result = VattiClipper.clip(subject, subject);
        assertEquals(resultPoints, result.points);

        // Using a a square as subject clip it with the
        // complex polygon. The square is bounding the 
        // complex polygom, so must return the complex one.

        clipPoints = subjectPoints;
        subjectPoints = new ArrayList<>(Arrays.asList(
            new Vector2D(0, 0),
            new Vector2D(0, 3),
            new Vector2D(3, 3),
            new Vector2D(3, 0)
        ));

        subject = new Polygon<>(subjectPoints);
        clip = new Polygon<>(clipPoints);
        result = VattiClipper.clip(subject, clip);

        System.err.println(result.points);
        assertEquals(resultPoints, result.points);
    }
} 